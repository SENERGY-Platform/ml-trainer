import json 
from copy import deepcopy

import ray
import mlflow
from darts import TimeSeries

from train import fit_and_evaluate_model
from tune import run_hyperparameter_tuning_for_each_model
from data.kafka.kafka import KafkaLoader
from data.dummy import DummyLoader
from db import store_model
from splitter import Splitter
from config import Config
from plot import log_plot

# Each training will reserve 1 CPU
@ray.remote(num_cpus=1)
def train_model(config, train_ts, test_ts, experiment_id, pipeline_name, mlflow_url):
    # Setup correct MLFLOW URL
    mlflow.set_tracking_uri(mlflow_url)

    config_copy = deepcopy(config)
    pipeline, metrics, pred_ts = fit_and_evaluate_model(train_ts, test_ts, config_copy)
    checkpoint = ray.air.checkpoint.Checkpoint.from_dict(
        {"model": pipeline}
    )

    # Log to MLFLOW
    run_name = f"{pipeline_name} - with optimized hyperparameters"
    mlflow.end_run()
    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name):
        mlflow.log_metrics(metrics)
        mlflow.log_params(config)
        log_plot(test_ts, pred_ts, mlflow)

    return metrics, checkpoint, config

def train_best_models_and_test(models, best_config_per_model, train_ts, test_ts, metric_direction, selection_metric, experiment_id, mlflow_url):
    jobs = []
    best_metric_value = None
    best_checkpoint = None
    best_config = None 

    # Run Hyperparametey Tuning for all models on Train TimeSeries
    for model in models:
        job_id = train_model.remote(best_config_per_model[model], train_ts, test_ts, experiment_id, model, mlflow_url)   
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

def create_dataloader():
    dataloader = KafkaLoader(Config.KSQL_SERVER_URL, Config.KAFKA_TOPIC_CONFIG, Config.EXPERIMENT_NAME)
    dataloader.connect()
    #dataloader = DummyLoader()
    dataloader.load_data()
    return dataloader

def create_experiment(exp_name):
    experiment_id = mlflow.create_experiment(exp_name)
    return experiment_id

if __name__ == '__main__':
    mlflow.set_tracking_uri(Config.MLFLOW_URL)
    
    models = Config.MODELS
    task = Config.TASK
    experiment_name = Config.EXPERIMENT_NAME
    selection_metric = Config.METRIC_FOR_SELECTION 
    metric_direction = Config.METRIC_DIRECTION
    experiment_id = create_experiment(experiment_name)

    dataloader = create_dataloader()
    data_df = dataloader.get_data()
    print(data_df)
    
    ts = TimeSeries.from_dataframe(data_df, time_col="time", value_cols="value")
    splitter = Splitter()
    train_ts, test_ts = splitter.single_split(ts)

    best_config_per_model = run_hyperparameter_tuning_for_each_model(models, experiment_name, selection_metric, train_ts, metric_direction)
    print(f'Best configs per model: {best_config_per_model}')

    # TODO train again on complete train ts and test against test_ts 
    best_metric_value, best_checkpoint, best_config = train_best_models_and_test(models, best_config_per_model, train_ts, test_ts, metric_direction, selection_metric, experiment_id, Config.MLFLOW_URL)
    print(f'Best value: {best_metric_value}, Best config: {best_config}')

    # Store best model checkpoint
    model_id = store_model(best_checkpoint, Config.USER_ID, best_config, experiment_name, Config.MODEL_ARTIFACT_NAME, task, Config.COMMIT)
    
    result = {
        'best_model_id': model_id,
        'best_config': best_config,
        'best_metric_value': best_metric_value
    }
    print(f"RESULT_START{json.dumps(result)}RESULT_END")