import json 

import mlflow

from parameter_tuning.tune import run_hyperparameter_tuning_for_each_model
from model_selection.selection import train_best_models_and_test
from data.loaders.load import get_data_loader
from data.preprocessors.load import get_preprocessor

from model_registry import store_model
from tasks.load import get_task
from config import Config


def get_data(data_loader_name, data_settings):
    dataloader = get_data_loader(data_loader_name, data_settings)
    return dataloader.get_data()

def create_experiment(exp_name):
    experiment_id = mlflow.create_experiment(exp_name)
    return experiment_id   

def preprocess_data(data, processor_name, frequency):
    # TODO config
    proc = get_preprocessor(processor_name, data, frequency)
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
    data_settings = config.DATA_SETTINGS
    data_loader_name = config.DATA_SOURCE
    preprocessor_name = config.PREPROCESSOR

    task = get_task(task_name, task_settings)
    data_df = get_data(data_loader_name, data_settings)

    # TODO configuration whether total consumption data or single value data 
    preprocessed_data = preprocess_data(data_df, preprocessor_name, task_settings.frequency)
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