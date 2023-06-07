import json 
from copy import deepcopy

import ray
import mlflow

from tune import tune_model, load_hyperparams
from train import fit_and_evaluate_model
from data.kafka.kafka import KafkaLoader
from data.dummy import DummyLoader
from db import store_model
from splitter import Splitter
from config import Config

@ray.remote
def evaluate_model_and_hyperparams(hyperparams, experiment_name, train_ts, config):
    return tune_model(hyperparams, experiment_name, train_ts, config)

def run_hyperparameter_tuning_for_each_model(models, experiment_name, selection_metric, train_ts, metric_direction, config):
    jobs = []
    best_config_per_model = {}
    job_id_to_model = {}

    # Run Hyperparametey Tuning for all models on Train TimeSeries
    for model in models:
        print(f'Start Hyperparamter Tuning for {model}')
        hyperparams = load_hyperparams(model)
        hyperparams['freq'] = 'H'
        hyperparams['pipeline'] = model
        job_id = evaluate_model_and_hyperparams.remote(hyperparams, experiment_name, train_ts, config)   
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
def train_model(config, train_ts, test_ts, experiment_name, pipeline_name):
    config_copy = deepcopy(config)
    pipeline, metrics = fit_and_evaluate_model(train_ts, test_ts, config_copy)
    checkpoint = ray.air.checkpoint.Checkpoint.from_dict(
        {"model": pipeline}
    )

    # TODO mlflow tracking here 
    experiment = mlflow.get_experiment_by_name(experiment_name)
    run_name = f"{pipeline_name} - with optimized hyperparameters"
    mlflow.end_run()
    with mlflow.start_run(experiment_id=experiment.experiment_id, run_name=run_name):
        mlflow.log_metrics(metrics)
        mlflow.log_params(config)

    return metrics, checkpoint, config

def train_best_models_and_test(models, best_config_per_model, train_ts, test_ts, metric_direction, selection_metric, experiment_name):
    jobs = []
    best_metric_value = None
    best_checkpoint = None
    best_config = None 

    # Run Hyperparametey Tuning for all models on Train TimeSeries
    for model in models:
        job_id = train_model.remote(best_config_per_model[model], train_ts, test_ts, experiment_name, model)   
        jobs.append(job_id)

    # Fetch and print the results of the tasks in the order that they complete.
    while jobs:
        # Use ray.wait to get the object ref of the first task that completes.
        done_ids, jobs = ray.wait(jobs)
        result_id = done_ids[0]
        tuning_result = ray.get(result_id)
        model_metrics, model_checkpoint, model_config = tuning_result
        model_metric_value = model_metrics[selection_metric]

        if (not best_metric_value) or \
            (metric_direction == 'min' and model_metric_value < best_metric_value) or \
            (metric_direction == 'max' and model_metric_value > best_metric_value):
            best_metric_value = model_metric_value
            best_checkpoint = model_checkpoint
            best_config = model_config

    return best_metric_value, best_checkpoint, best_config

def create_dataloader(config):
    #dataloader = KafkaLoader(config.KSQL_SERVER_URL, config.KAFKA_TOPIC_CONFIG, config.EXPERIMENT_NAME)
    #dataloader.connect()
    dataloader = DummyLoader()
    dataloader.load_data()
    return dataloader

if __name__ == '__main__':
    config = Config()
    mlflow.set_tracking_uri(config.MLFLOW_URL)
    
    models = config.MODELS
    task = config.TASK
    experiment_name = config.EXPERIMENT_NAME
    selection_metric = config.METRIC_FOR_SELECTION 
    metric_direction = config.METRIC_DIRECTION

    dataloader = create_dataloader(config)

    splitter = Splitter()
    train_ts, test_ts = splitter.single_split(dataloader.get_data())

    best_config_per_model = run_hyperparameter_tuning_for_each_model(models, experiment_name, selection_metric, train_ts, metric_direction, config)
    print(f'Best configs per model: {best_config_per_model}')

    # TODO train again on complete train ts and test against test_ts 
    best_metric_value, best_checkpoint, best_config = train_best_models_and_test(models, best_config_per_model, train_ts, test_ts, metric_direction, selection_metric, experiment_name)
    print(f'Best value: {best_metric_value}, Best config: {best_config}')

    # Store best model checkpoint
    model_id = store_model(best_checkpoint, config.USER_ID, best_config['pipeline'], experiment_name, config.MODEL_ARTIFACT_NAME, task)
    
    result = {
        'best_model_id': model_id,
        'best_config': best_config,
        'best_metric_value': best_metric_value
    }
    print(f"RESULT_START{json.dumps(result)}RESULT_END")