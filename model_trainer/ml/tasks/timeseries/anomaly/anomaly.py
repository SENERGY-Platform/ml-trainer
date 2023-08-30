from tasks.timeseries.task import TimeSeriesTask
from tasks.timeseries.anomaly.plots import plot_losses, plot_reconstructions

from toolbox.anomaly_detection.load import get_pipeline
import numpy as np 
from sklearn.model_selection import train_test_split

class AnomalyTask(TimeSeriesTask):
    def __init__(self, task_settings) -> None:
        super().__init__(task_settings.frequency)
        self.window_size = task_settings.window_size
        self.stride = task_settings.stride

    def fit_and_evaluate_model(self, train_data, test_data, config):
        # data: numpy array [NUMBER_SAMPLE x WINDOW_SIZE] 

        pipeline_name = config['pipeline']

        # Remove pipeline name to pass remaining configs as model parameters
        del config['pipeline']
        del config['freq']
        config['window_length'] = self.window_size
        config['plot_enabled'] = False
        
        pipeline = get_pipeline(pipeline_name)(**config)

        train_data, validation_data = self.split_data(train_data)
        pipeline.fit(train_data, validation_data)

        reconstructions, anomaly_indices, normal_indices, test_losses = pipeline.predict(test_data, 0.3)
        
        metrics = {
            "losses": test_losses.sum().item()
        }

        normal_recons_plot = plot_reconstructions(reconstructions, normal_indices, test_data, "Normal")
        anomaly_recons_plot = plot_reconstructions(reconstructions, anomaly_indices, test_data, "Anomaly")

        losses_hist = plot_losses(test_losses)
        plots = [losses_hist, normal_recons_plot, anomaly_recons_plot]

        return pipeline, metrics, plots

    def convert_data(self, data_df):
        values = list(data_df['value'])
        windows = []

        start = 0
        end = self.window_size

        while end < len(values):
            window = values[start:end]
            windows.append(window)
            start += self.stride
            end = start + self.window_size

        return np.asarray(windows)

    def split_data(self, data):
        return train_test_split(data, shuffle=True, test_size=0.25)

    def get_pipeline_hyperparams(self, pipeline_name, train_ts):
        return get_pipeline(pipeline_name).get_hyperparams(self.frequency, train_ts)
