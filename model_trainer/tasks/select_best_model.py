import os
print(f"Number of CPUs in this system: {os.cpu_count()}")
import json 
from copy import deepcopy

import ray
import mlflow
from ray import air, tune
from ray.air.integrations.mlflow import setup_mlflow

from tune import tune_model, load_hyperparams
from train import fit_and_evaluate_model
from data import DataLoader
from db import store_model
from splitter import Splitter

@ray.remote
def evaluate_model_and_hyperparams(hyperparams, experiment_name, train_ts):
    return tune_model(hyperparams, experiment_name, train_ts)

def run_hyperparameter_tuning_for_each_model(models, experiment_name, selection_metric, train_ts, metric_direction):
    jobs = []
    best_config_per_model = {}
    job_id_to_model = {}

    # Run Hyperparametey Tuning for all models on Train TimeSeries
    for model in models:
        print(f'Start Hyperparamter Tuning for {model}')
        hyperparams = load_hyperparams(model)
        hyperparams['freq'] = 'H'
        hyperparams['pipeline'] = model
        job_id = evaluate_model_and_hyperparams.remote(hyperparams, experiment_name, train_ts)   
        jobs.append(job_id)
        job_id_to_model[job_id] = model

    # Fetch and print the results of the tasks in the order that they complete.
    while jobs:
        # Use ray.wait to get the object ref of the first task that completes.
        done_ids, jobs = ray.wait(jobs)
        result_id = done_ids[0]
        model = job_id_to_model[result_id]
        tuning_result = ray.get(result_id)
        print(tuning_result)
        
        best_model_result = tuning_result.get_best_result(selection_metric, metric_direction)
        best_config_per_model[model] = best_model_result.config
        
        #best_metric_value_per_model[model] = best_model_result.metrics[selection_metric]
        #best_checkpoint_per_model[model] = best_model_result.checkpoint

    return best_config_per_model

@ray.remote
def train_model(config, train_ts, test_ts):
    config_copy = deepcopy(config)
    pipeline, metrics = fit_and_evaluate_model(train_ts, test_ts, config_copy)
    checkpoint = ray.air.checkpoint.Checkpoint.from_dict(
        {"model": pipeline}
    )

    # TODO mlflow tracking here 
    mlflow.log_metric()

    return metrics, checkpoint, config

def train_best_models_and_test(models, best_config_per_model, train_ts, test_ts, metric_direction, selection_metric):
    jobs = []
    best_metric_value = None
    best_checkpoint = None
    best_config = None 

    # Run Hyperparametey Tuning for all models on Train TimeSeries
    for model in models:
        job_id = train_model.remote(best_config_per_model[model], train_ts, test_ts)   
        jobs.append(job_id)

    # Fetch and print the results of the tasks in the order that they complete.
    while jobs:
        # Use ray.wait to get the object ref of the first task that completes.
        done_ids, jobs = ray.wait(jobs)
        result_id = done_ids[0]
        tuning_result = ray.get(result_id)
        model_metrics, model_checkpoint, model_config = tuning_result
        model_metric_value = model_metrics[selection_metric]
        print(model_metric_value)

        if (not best_metric_value) or \
            (metric_direction == 'min' and model_metric_value < best_metric_value) or \
            (metric_direction == 'max' and model_metric_value > best_metric_value):
            best_metric_value = model_metric_value
            best_checkpoint = model_checkpoint
            best_config = model_config

    return best_metric_value, best_checkpoint, best_config

if __name__ == '__main__':
    MLFLOW_URL = os.environ['MLFLOW_URL']
    mlflow.set_tracking_uri(MLFLOW_URL)
    
    models = os.environ['MODELS'].split(';')
    user_id = os.environ['USER_ID']
    task = os.environ['TASK']
    experiment_name = os.environ['EXPERIMENT_NAME']
    model_artifcat_name = os.environ['MODEL_ARTIFACT_NAME']
    selection_metric = os.environ.get('METRIC_FOR_SELECTION', 'mae') 
    metric_direction = os.environ.get("METRIC_DIRECTION", "min")

    dataloader = DataLoader()
    dataloader.load_data()
    
    splitter = Splitter()
    train_ts, test_ts = splitter.single_split(dataloader.get_data())

    best_config_per_model = run_hyperparameter_tuning_for_each_model(models, experiment_name, selection_metric, train_ts, metric_direction)
    print(f'Best configs per model: {best_config_per_model}')

    # TODO train again on complete train ts and test against test_ts 
    best_metric_value, best_checkpoint, best_config = train_best_models_and_test(models, best_config_per_model, train_ts, test_ts, metric_direction, selection_metric)
    print(f'Best value: {best_metric_value}, Best config: {best_config}')

    # Store best model checkpoint
    model_id = store_model(best_checkpoint, user_id, best_config['pipeline'], experiment_name, model_artifcat_name, task)
    
    result = {
        'best_model_id': model_id,
        'best_config': best_config,
        'best_metric_value': best_metric_value
    }
    print(f"RESULT_START{json.dumps(result)}RESULT_END")