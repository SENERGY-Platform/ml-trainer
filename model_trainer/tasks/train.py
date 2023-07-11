import ray
import mlflow
from toolbox.estimation.load import get_pipeline
from toolbox.estimation.evaluation.calc_scores import calc_scores
import matplotlib.pyplot as plt 


def fit_and_evaluate_model(train_ts, test_ts, config):
    """
    Train a single model on TRAIN with parameter specification and evaluate on TEST. No mlflow logging here!
    """
    pipeline_name = config['pipeline']

    # Remove pipeline name to pass remaining configs as model parameters
    del config['pipeline']

    pipeline = get_pipeline(pipeline_name)(**config)
    pipeline.fit(train_ts)

    # Evaluate on Test
    n_steps = len(test_ts)
    pred_ts = pipeline.predict(n_steps)
    metrics = calc_scores(test_ts, pred_ts)

    return pipeline, metrics, pred_ts



