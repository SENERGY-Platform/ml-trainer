import tempfile
from pathlib import Path
import pickle 

import mlflow
from ray import air, tune
from data.loaders.load import get_data_loader
from ray.air.integrations.mlflow import MLflowLoggerCallback
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from ray.air import session

from config import Config


def get_data(data_loader_name, data_settings):
    dataloader = get_data_loader(data_loader_name, data_settings)
    return dataloader.get_data()

def create_experiment(exp_name):
    experiment_id = mlflow.create_experiment(exp_name)
    return experiment_id   

'''Glätten, Shiften, Padden'''


def smoothen(load_curve, window_length):# Berechnet exponentiale Glättung einer Lastkurve (In- und Output als array). Glättung ist notwendig, um später Optimierungs-Algorithmen anwenden zu können.
    window_length = window_length #Parameter für die Glättung. Muss für jede Kurve einzeln gewählt werden.
    df = pd.DataFrame(load_curve)
    return np.array(df.rolling(window=int(window_length), win_type="exponential", center=True).mean().fillna(value=0)).flatten()

def round_shifts(shift_lengths, decimals=2): # Rundet die Shift-Werte auf Vielfache der resolution, damit die Lastgangkurven nach den Shifts weiter auf den gleichen Stützstellen definiert sind.
    return np.array(shift_lengths).round(decimals=decimals).flatten()

def end_pad_zeros(list_of_shifted_load_curves): # Padded die geshifteten Lastgang-Kurven, damit nach dem Shiften wieder alle Kurven die gleiche Länge haben.
    aux_list = []
    max_length = max([len(shifted_load_curve) for shifted_load_curve in list_of_shifted_load_curves])
    for shifted_load_curve in list_of_shifted_load_curves:
        padded_shifted_load_curve = np.hstack((shifted_load_curve, np.zeros(max_length-len(shifted_load_curve))))
        aux_list.append(padded_shifted_load_curve)
    return np.vstack(aux_list)

def shift_loads(array_of_loads, *shift_lengths):#
    rounded_shift_lengths = round_shifts(shift_lengths)
    aux_list = []
    for i in range(len(rounded_shift_lengths)):
        load_curve = array_of_loads[i]
        if rounded_shift_lengths[i] >= 0:
            start_zeros = np.zeros(int(rounded_shift_lengths[i]*100))
            shifted_load = np.hstack((start_zeros, load_curve))
        else:
            shifted_load = load_curve[-int(rounded_shift_lengths[i]*100):]
        aux_list.append(shifted_load)
    padded_shifted_loads_array = end_pad_zeros(aux_list)
    return padded_shifted_loads_array
    

'''Aggregieren der geshifteten Lastgang-Kurven und Max-Berechnung'''

def load_sum(array):# Berechnet die Summe der Kurven, die als Zeilen in array abgelegt sind.
    return np.sum(array, axis=0)

def compute_load_peak(curve):# Berechnet das Maximum einer Kurve (gegeben als array). Das ist keine komplexe Berechnung. Hier kann einfach das Maximum über das Array berechnet werden.
    return np.max(curve)

def max_of_sum(array):# Berechnet das Maximum der Summe der Kurven, die als Zeilen in array abgelegt sind.
    combined_loads = load_sum(array)
    return compute_load_peak(combined_loads)

'''Berechnung der target function für die Minimierung (berechnet wird der maximale Peak der Last-Aggregation der geshifteten Kurven in Abhängigkeit der Shift-Weiten)'''

def target_function(array_of_loads, *shift_lengths):
    array_of_smoothened_load_curves = np.vstack([smoothen(array_of_loads[i],smoothing_window_lengths[i]) for i in range(array_of_loads.shape[0])]) 
    # Berechnet die Glätungen der einzelne Last-Kurven, die als Zeilen in array_of_loads abgelegt sind.  
    padded_shifted_loads = shift_loads(array_of_smoothened_load_curves, *shift_lengths)
    # Berechnet die Shifts der geglätteten Kurven und padded mit Nullen am Ende
    return max_of_sum(padded_shifted_loads)# Berechnet das Maximum der Summe der geshifteten Kurven.

'''Approximimerte Lösung des Minimierungs-Problems'''

def find_optim_shift_loads_per_config(loads, parameter_config):
    print("Run optimization")
    OptimizeResult = minimize(lambda x: target_function(loads, *x), parameter_config['x0'], method='Powell', options={'xtol': parameter_config['xtol'], 'ftol': parameter_config['ftol']})
    max_sum = target_function(loads, *(OptimizeResult.x))
    return OptimizeResult.x, max_sum

def tune_with_param(parameter_config, loads):
    _, max_load_sum = find_optim_shift_loads_per_config(loads, parameter_config)
    session.report({
        "max_load_sum": max_load_sum
    })

def run_across_hyperparams(hyperparams, experiment_name, loads):
    # Define a tuner object.
    tuner = tune.Tuner(
            tune.with_parameters(tune_with_param, loads=loads),
            param_space=hyperparams,
            run_config=air.RunConfig(
                name="tune_model",
                # Set Ray Tune verbosity. Print summary table only with levels 2 or 3.
                verbose=2,
                callbacks=[MLflowLoggerCallback(
                    tracking_uri=Config.MLFLOW_URL,
                    experiment_name=experiment_name,
                    save_artifact=True,
                )]
            )
    )

    # Fit the tuner object.
    results = tuner.fit()
    return results

def store_shifted_loads(experiment_id, optimal_shifted_loads):
    print('Store optimal shifted loads')
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir, "features.pickle")
        with open(path, 'wb') as f:
            pickle.dump(optimal_shifted_loads, f)

        run_name = f"with optimized hyperparameters"
        mlflow.end_run()
        with mlflow.start_run(experiment_id=experiment_id, run_name=run_name):
            mlflow.log_artifact(path)

def testload(s, load_domain, value, peak_length, valley_length):
    shape = load_domain.shape
    aux_list = []
    for k in range(20):
        aux_list.append(np.logical_and((k*peak_length+k*valley_length+s)*np.ones(shape) <= load_domain, load_domain < ((k+1)*peak_length+k*valley_length+s)*np.ones(shape)).astype(float))
    return value*np.sum(np.array(aux_list), axis=0)

if __name__ == '__main__':
    '''Parameter, die während des Pre-Processings der einzelnen Lastgangkurven bestimmt werden müssen'''
    number_of_loads = 3
    # Anzahl der verschiedenen Lastgangkurven.

    resolution = 1/100
    # Auflösung der Lastgang-Kurven. Es ist wichtig, diese Größe zu fixieren um später die korrekten Verschiebungen der einzelnen Kurven zu berechnen.

    smoothing_window_lengths = [100, 100, 200]
    # Für die Glättung der einzelnen Lastgang-Kurven gibt es einen wichtigen Hyper-Paramter: die window_length. UnterUmständen ist es sinnvoll jede Kurve mit einer
    # separaten Wahl der window_length zu glätten. smoothing_window_lengths enthält die window_length Wahlen für die einzelnen Kurven.

    config = Config()
    mlflow.set_tracking_uri(config.MLFLOW_URL)
    experiment_id = create_experiment(config.EXPERIMENT_NAME)
    data_settings = config.DATA_SETTINGS
    #loads1 = get_data(config.DATA_SOURCE, data_settings)
    
    # Dieses array enthält als Zeilen die einzelnen Lastgangkurven. Alle Kurven sind über die selben Stützstellen definiert.
    #loads_matrix = np.asarray([loads1['value'].to_numpy(), loads1['value'].to_numpy()])
    load_domain = np.arange(-1,50,0.01)
    values = [1, 1, 1]
    peak_lengths = [1, 1, 2]
    valley_lengths = [3, 3, 2]
    loads_matrix = np.asarray([testload(0, load_domain, values[0], peak_lengths[0], valley_lengths[0]),
    testload(0, load_domain, values[1], peak_lengths[1], valley_lengths[1]),
    testload(0, load_domain, values[2], peak_lengths[2], valley_lengths[2])])

    hyperparams = {
        'xtol': 0.0000001,
        'ftol': 0.0000001,
        'x0': tune.grid_search([np.random.uniform(-5, 5, size=(number_of_loads,)) for _ in range(number_of_loads)]) # Startpunkt des Minimierungs-Algorithmus. Wichtigster Hyper-Paramter.
    }
    tuning_result = run_across_hyperparams(hyperparams, config.EXPERIMENT_NAME, loads_matrix)
    best_result = tuning_result.get_best_result("max_load_sum", "min")
    best_config = best_result.config
    print(f"Best Parameters: {best_config}")

    optimal_shifted_loads, _ = find_optim_shift_loads_per_config(loads_matrix, best_config)
    print(optimal_shifted_loads)
    store_shifted_loads(experiment_id, optimal_shifted_loads)