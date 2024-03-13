from copy import deepcopy

import ray
import mlflow 
import matplotlib.pyplot as plt 

# Each training will reserve 1 CPU
@ray.remote(num_cpus=1)
def train_best_model(config, train_data, test_data, experiment_id, pipeline_name, mlflow_url, task):
    # Train the model with tuned hyperparameters and evaluate on test data

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
        
        # Close all figures to prevent memory leaks
        plt.close("all")

    return metrics, checkpoint, config

def train_best_models_and_test(
    models, 
    best_config_per_model, 
    train_ts, 
    test_ts, 
    metric_direction, 
    selection_metric, 
    experiment_id, 
    mlflow_url, 
    task
):
    jobs = []
    best_metric_value = None
    best_checkpoint = None
    best_config = None 

    for model in models:
        job_id = train_best_model.remote(best_config_per_model[model], train_ts, test_ts, experiment_id, model, mlflow_url, task)   
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
