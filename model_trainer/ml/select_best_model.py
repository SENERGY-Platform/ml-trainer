import json 
from copy import deepcopy

import ray
import mlflow

from parameter_tuning.tune import run_hyperparameter_tuning_for_each_model
from data.loaders.kafka.kafka import KafkaLoader
from data.loaders.dummy import DummyLoader
from data.preprocessors.load import get_preprocessor

from db import store_model
from tasks.load import get_task
from config import Config

# Each training will reserve 1 CPU
@ray.remote(num_cpus=1)
def train_model(config, train_data, test_data, experiment_id, pipeline_name, mlflow_url, task):
    # Setup correct MLFLOW URL
    mlflow.set_tracking_uri(mlflow_url)

    config_copy = deepcopy(config)
    pipeline, metrics, plots = task.fit_and_evaluate_model(train_data, test_data, config_copy)
    checkpoint = ray.air.checkpoint.Checkpoint.from_dict(
        {"model": pipeline}
    )

    # Log to MLFLOW
    run_name = f"{pipeline_name} - with optimized hyperparameters"
    mlflow.end_run()
    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name):
        mlflow.log_metrics(metrics)
        mlflow.log_params(config)

        for i, plot in enumerate(plots):
            mlflow.log_figure(plot, f'plots/plot{i}.png')

    return metrics, checkpoint, config

def train_best_models_and_test(models, best_config_per_model, train_ts, test_ts, metric_direction, selection_metric, experiment_id, mlflow_url, task):
    jobs = []
    best_metric_value = None
    best_checkpoint = None
    best_config = None 

    for model in models:
        job_id = train_model.remote(best_config_per_model[model], train_ts, test_ts, experiment_id, model, mlflow_url, task)   
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

def get_data(ksql_url, data_settings, exp_name):
    #dataloader = KafkaLoader(ksql_url, data_settings, exp_name)
    dataloader = DummyLoader()
    dataloader.connect()
    dataloader.load_data()
    return dataloader.get_data()

def create_experiment(exp_name):
    experiment_id = mlflow.create_experiment(exp_name)
    return experiment_id   

def preprocess_data(data, processor_name, frequency):
    # TODO config
    proc = get_preprocessor(processor_name)(data, frequency)
    return proc.run()

if __name__ == '__main__':
    config = Config()
    mlflow.set_tracking_uri(config.MLFLOW_URL)
    
    models = config.MODELS
    task_name = config.TASK
    experiment_name = config.EXPERIMENT_NAME
    selection_metric = config.METRIC_FOR_SELECTION 
    metric_direction = config.METRIC_DIRECTION
    task_settings = config.TASK_SETTINGS
    experiment_id = create_experiment(experiment_name)

    task = get_task(task_name, task_settings)

    data_df = get_data(config.KSQL_SERVER_URL, config.DATA_SETTINGS, experiment_name)

    # TODO configuration whether total consumption data or single value data 
    preprocessed_data = preprocess_data(data_df, "", task_settings.frequency)
    task_converted_data = task.convert_data(preprocessed_data)
    train_data, test_data = task.split_data(task_converted_data)

    best_config_per_model = run_hyperparameter_tuning_for_each_model(models, experiment_name, selection_metric, train_data, metric_direction, task, task_settings.frequency)
    print(f'Best configs per model: {best_config_per_model}')

    best_metric_value, best_checkpoint, best_config = train_best_models_and_test(models, best_config_per_model, train_data, test_data, metric_direction, selection_metric, experiment_id, config.MLFLOW_URL, task)
    print(f'Best value: {best_metric_value}, Best config: {best_config}')

    # Store best model checkpoint
    model_id = store_model(best_checkpoint, config.USER_ID, best_config, experiment_name, config.MODEL_ARTIFACT_NAME, task, config.COMMIT)
    
    result = {
        'best_model_id': model_id,
        'best_config': best_config,
        'best_metric_value': best_metric_value
    }
    print(f"RESULT_START{json.dumps(result)}RESULT_END")