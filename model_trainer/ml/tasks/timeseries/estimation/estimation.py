from tasks.timeseries.estimation.metrics import calc_metrics
from tasks.timeseries.estimation.plot import generate_plot
from tasks.timeseries.task import TimeSeriesTask
from data.splitter.splitter import Splitter

from toolbox.estimation.load import get_pipeline
from darts import TimeSeries


class ConsumptionEstimationTask(TimeSeriesTask):
    def __init__(self, task_settings) -> None:
        super().__init__(task_settings.frequency)

    def fit_and_evaluate_model(self, train_ts, test_ts, config):
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
        metrics = calc_metrics(test_ts, pred_ts)
        plot = generate_plot(test_ts, pred_ts)

        return pipeline, metrics, [plot]

    def split_data(self, ts):
        splitter = Splitter()
        train_ts, test_ts = splitter.single_split(ts)
        return train_ts, test_ts

    def convert_data(self, preprocessed_data_df):
        data = preprocessed_data_df.reset_index()
        return TimeSeries.from_dataframe(data, time_col="time", value_cols="value")

    def get_pipeline_hyperparams(self, pipeline_name, train_ts):
        return get_pipeline(pipeline_name).get_hyperparams(self.frequency, train_ts)
