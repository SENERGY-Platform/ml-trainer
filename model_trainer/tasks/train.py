import os
print(f"Number of CPUs in this system: {os.cpu_count()}")

import ray
from ray.air import session
import mlflow
from darts.utils.model_selection import train_test_split
from toolbox.estimation import pipelines
from toolbox.estimation.evaluation.calc_scores import calc_scores
import matplotlib.pyplot as plt 

from data import load_est_data


def load_pipeline(pipeline_name):
    return getattr(pipelines, pipeline_name)

def fit_and_evaluate_model(train_ts, n_steps, ts, config):
    pipeline_name = config['pipeline']

    # Remove pipeline name to pass remaining configs as model parameters
    del config['pipeline']

    pipeline = load_pipeline(pipeline_name)(**config)
    pipeline.fit(train_ts)

    # Evaluate on Test
    pred_ts = pipeline.predict(n_steps)
    metrics = calc_scores(ts, pred_ts)

    # Plot
    ts.plot(label="expected")
    pred_ts.plot(label="prediction")
    mlflow.log_figure(plt.gcf(), 'plots/predictions.png')
    return pipeline, metrics

def train(config: dict) -> None:
    ts = load_est_data()

    # Single Split TODO CV
    train_ts, test_ts = train_test_split(ts, test_size=0.25)
    n_steps = len(test_ts)
    
    pipeline, metrics = fit_and_evaluate_model(train_ts, n_steps, ts, config)
    
    # Define a model checkpoint using AIR API.
    # https://docs.ray.io/en/latest/tune/tutorials/tune-checkpoints.html
    checkpoint = ray.air.checkpoint.Checkpoint.from_dict(
        {"model": pipeline}
    )

    # Save checkpoint and report back metrics, using ray.air.session.report()
    # The metrics you specify here will appear in Tune summary table.
    # They will also be recorded in Tune results under `metrics`.
    
    # MlFlow call back will automatically save hyperparameter, metrics and checkpoints
    session.report(metrics, checkpoint=checkpoint)


