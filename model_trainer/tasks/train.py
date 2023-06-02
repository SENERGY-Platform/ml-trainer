import os
print(f"Number of CPUs in this system: {os.cpu_count()}")

import ray
import mlflow
from toolbox.estimation import pipelines
from toolbox.estimation.evaluation.calc_scores import calc_scores
import matplotlib.pyplot as plt 


def load_pipeline(pipeline_name):
    return getattr(pipelines, pipeline_name)

def fit_and_evaluate_model(train_ts, test_ts, config):
    pipeline_name = config['pipeline']

    # Remove pipeline name to pass remaining configs as model parameters
    del config['pipeline']

    pipeline = load_pipeline(pipeline_name)(**config)
    pipeline.fit(train_ts)

    # Evaluate on Test
    n_steps = len(test_ts)
    pred_ts = pipeline.predict(n_steps)
    metrics = calc_scores(test_ts, pred_ts)

    # Plot
    test_ts.plot(label="expected")
    pred_ts.plot(label="prediction")
    mlflow.log_figure(plt.gcf(), 'plots/predictions.png')
    return pipeline, metrics



