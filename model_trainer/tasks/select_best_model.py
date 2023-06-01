import os
print(f"Number of CPUs in this system: {os.cpu_count()}")
import json 

import ray
import mlflow
from ray import air, tune
from ray.air.integrations.mlflow import setup_mlflow

from tune import tune_model, load_hyperparams
from db import store_model


@ray.remote
def evaluate_model_and_hyperparams(hyperparams, experiment_name):
    return tune_model(hyperparams, experiment_name)

if __name__ == '__main__':
    MLFLOW_URL = os.environ['MLFLOW_URL']
    mlflow.set_tracking_uri(MLFLOW_URL)
    
    models = os.environ['MODELS'].split(';')
    user_id = os.environ['USER_ID']
    task = os.environ['TASK']
    experiment_name = os.environ['EXPERIMENT_NAME']
    model_artifcat_name = os.environ['MODEL_ARTIFACT_NAME']    

    jobs = []
    best_metric_value = 0
    best_checkpoint = None
    best_config = {}

    for model in models:
        hyperparams = load_hyperparams(model)
        hyperparams['freq'] = 'H'
        hyperparams['pipeline'] = model
        job_id = evaluate_model_and_hyperparams.remote(hyperparams, experiment_name)   
        jobs.append(job_id)

    
    # Fetch and print the results of the tasks in the order that they complete.
    while jobs:
        # Use ray.wait to get the object ref of the first task that completes.
        done_ids, jobs = ray.wait(jobs)
        result_id = done_ids[0]
        tuning_result = ray.get(result_id)
        print(tuning_result)
        
        best_model_result = tuning_result.get_best_result("mae", "min")
        best_model_metric_value = best_model_result.metrics["mae"]
        best_model_config = best_model_result.config
        best_model_checkpoint = best_model_result.checkpoint

        if best_model_metric_value > best_metric_value:
            best_config = best_model_config
            best_metric_value = best_model_metric_value
            best_checkpoint = best_model_checkpoint
    
    # Store best model checkpoint
    model_id = store_model(best_checkpoint, user_id, model, experiment_name, model_artifcat_name, task)
    
    result = {
        'best_model_id': model_id,
        'best_config': best_config,
        'best_metric_value': best_metric_value
    }
    print(f"RESULT_START{json.dumps(result)}RESULT_END")