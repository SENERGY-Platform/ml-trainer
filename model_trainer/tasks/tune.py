from copy import deepcopy
import uuid 

import mlflow
import ray
from ray import air, tune
from ray.air.integrations.mlflow import setup_mlflow, MLflowLoggerCallback
from ray.air import session
import matplotlib.pyplot as plt 


from toolbox.estimation import pipelines
from train import fit_and_evaluate_model
from splitter import Splitter
from config import Config

# Detect already running ray on node
ray.init(address="auto", ignore_reinit_error=True)

def run_hyperparameter_tuning_for_each_model(models, experiment_name, selection_metric, train_ts, metric_direction):
    # TODO: Multiple Tune jobs on one cluster are not supported yet, as Tune takes all cluster ressources
    #jobs = []
    #job_id_to_model = {}
    best_config_per_model = {}

    # Run Hyperparametey Tuning for all models on Train TimeSeries
    for model in models:
        print(f'Start Hyperparamter Tuning for {model}')
        hyperparams = load_hyperparams(model)
        hyperparams['freq'] = 'H'
        hyperparams['pipeline'] = model

        tuning_result = tune_model(hyperparams, experiment_name, train_ts)   
        best_model_result = tuning_result.get_best_result(selection_metric, metric_direction)
        best_config_per_model[model] = best_model_result.config
        
        #best_metric_value_per_model[model] = best_model_result.metrics[selection_metric]
        #best_checkpoint_per_model[model] = best_model_result.checkpoint
        
        #job_id = evaluate_model_and_hyperparams.remote(hyperparams, experiment_name, train_ts, config)   
        #jobs.append(job_id)
        #job_id_to_model[job_id] = model

    # Fetch and print the results of the tasks in the order that they complete.
    #while jobs:
        # Use ray.wait to get the object ref of the first task that completes.
        #done_ids, jobs = ray.wait(jobs)
        #result_id = done_ids[0]
        #model = job_id_to_model[result_id]
        #tuning_result = ray.get(result_id)
        #print(tuning_result)
        
    return best_config_per_model

def load_hyperparams(pipeline_name):
    model = getattr(pipelines, pipeline_name)
    hyperparams = model.get_hyperparams()
    ray_params = {}

    for param, values in hyperparams.items():
        ray_params[param] = tune.grid_search(values)
    
    return ray_params

def train(config, ts=None, mlflow_url=None):
    try:
        mlflow.set_tracking_uri(mlflow_url)

        # Setup MLFlow to use correct Server
        #mlflow_config['run_name'] = str(uuid.uuid4())
        #setup_mlflow(**mlflow_config)

        splitter = Splitter()
        train_ts, test_ts = splitter.single_split(ts)
        
        # Make a deep copy which can be passed to the model 
        # So that original config will be logged by ray and nothing is missing
        config_copy = deepcopy(config)
        
        pipeline, metrics, pred_ts = fit_and_evaluate_model(train_ts, test_ts, config_copy)
        
        # Log plots TODO not working, artifacts are not added to the trial run but to a completly new run in default
        # test_ts.plot(label="expected")
        # pred_ts.plot(label="prediction")
        # mlflow.log_figure(plt.gcf(), 'plots/predictions.png')   
        
        # Define a model checkpoint -> add to session.report - right now not needed 
        #checkpoint = ray.air.checkpoint.Checkpoint.from_dict(
        #    {"model": pipeline}
        #)
        
        # MlFlow call back will automatically save hyperparameter, metrics and checkpoints
        session.report(metrics)

    except Exception as e:
        raise Exception(str(e))

#@ray.remote
def tune_model(hyperparams, experiment_name, ts):
    # Define a tuner object.
    tuner = tune.Tuner(
            tune.with_parameters(train, ts=ts, mlflow_url=Config.MLFLOW_URL),
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
