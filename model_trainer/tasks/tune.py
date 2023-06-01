import os
print(f"Number of CPUs in this system: {os.cpu_count()}")
import json 

import ray
from ray import air, tune
from ray.air.integrations.mlflow import MLflowLoggerCallback
import mlflow
from toolbox.estimation import pipelines
from train import train
from db import store_model

MLFLOW_URL = os.environ['MLFLOW_URL']
ray.init(address="auto", ignore_reinit_error=True)

def load_hyperparams(pipeline_name):
    model = getattr(pipelines, pipeline_name)
    hyperparams = model.get_hyperparams()
    ray_params = {}

    for param, values in hyperparams.items():
        ray_params[param] = tune.grid_search(values)
    
    return ray_params

def tune_model(hyperparams, experiment_name):
    # Define a tuner object.
    tuner = tune.Tuner(
            train,
            param_space=hyperparams,
            run_config=air.RunConfig(
                name="tune_model",
                # Set Ray Tune verbosity. Print summary table only with levels 2 or 3.
                verbose=2,
                callbacks=[
                    MLflowLoggerCallback(
                        tracking_uri=MLFLOW_URL,
                        registry_uri=MLFLOW_URL,
                        experiment_name=experiment_name,
                        save_artifact=True,
                    )
                ],
            ),
    )

    # Fit the tuner object.
    results = tuner.fit()
    return results
