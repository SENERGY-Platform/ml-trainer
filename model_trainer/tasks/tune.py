from copy import deepcopy

import ray
from ray import air, tune
from ray.air.integrations.mlflow import MLflowLoggerCallback
from ray.air import session

from toolbox.estimation import pipelines
from train import fit_and_evaluate_model
from splitter import Splitter

# Detect already running ray on node
ray.init(address="auto", ignore_reinit_error=True)

def load_hyperparams(pipeline_name):
    model = getattr(pipelines, pipeline_name)
    hyperparams = model.get_hyperparams()
    ray_params = {}

    for param, values in hyperparams.items():
        ray_params[param] = tune.grid_search(values)
    
    return ray_params

def train(config, ts):
    splitter = Splitter()
    train_ts, test_ts = splitter.single_split(ts)
    
    # Make a deep copy which can be passed to the model 
    # So that original config will be logged by ray and nothing is missing
    config_copy = deepcopy(config)
    
    pipeline, metrics = fit_and_evaluate_model(train_ts, test_ts, config_copy)
    
    # Define a model checkpoint -> add to session.report - right now not needed 
    #checkpoint = ray.air.checkpoint.Checkpoint.from_dict(
    #    {"model": pipeline}
    #)

    # Save checkpoint and report back metrics, using ray.air.session.report()
    # The metrics you specify here will appear in Tune summary table.
    # They will also be recorded in Tune results under `metrics`.
    
    # MlFlow call back will automatically save hyperparameter, metrics and checkpoints
    session.report(metrics)

def tune_model(hyperparams, experiment_name, ts, config):
    # Define a tuner object.
    tuner = tune.Tuner(
            tune.with_parameters(train, ts=ts),
            param_space=hyperparams,
            run_config=air.RunConfig(
                name="tune_model",
                # Set Ray Tune verbosity. Print summary table only with levels 2 or 3.
                verbose=2,
                callbacks=[
                    MLflowLoggerCallback(
                        tracking_uri=config.MLFLOW_URL,
                        registry_uri=config.MLFLOW_URL,
                        experiment_name=experiment_name,
                        save_artifact=True,
                    )
                ],
            ),
    )

    # Fit the tuner object.
    results = tuner.fit()
    return results
