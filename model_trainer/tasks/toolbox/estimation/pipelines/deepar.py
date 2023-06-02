from gluonts.torch import DeepAREstimator
from toolbox.estimation.pipelines.helper import convert_to_gluon_pandas_dataset
import pandas as pd 
import numpy as np 

class DeepAR():
    def __init__(self, freq, add_time_covariates, **kwargs) -> None:
        self.kwargs = kwargs
        self.model = DeepAREstimator(trainer=Trainer(epochs=5), **kwargs)


    def fit(self, train_ts, target_column_name='target'):
        self.training_dataset = convert_to_gluon_pandas_dataset(train_ts, target_column_name)
        self.model.train(self.training_dataset)
        
    def predict(self, number_steps):
        train_dataset = convert_to_gluon_pandas_dataset(self.training_dataset)

        if number_steps > self.kwargs['prediction_length']:
            pass # TODO

        # use last context_length steps from train set to predict
        preds = self.model.predict(train_dataset)
        item = preds[0]
        mean_value_per_timestep = item.samples.mean(axis=0)
        p10_per_timestep = np.percentile(item.samples, 10, axis=0)
        p90_per_timestep = np.percentile(item.samples, 90, axis=0)
        date_per_timestep = pd.date_range(start=item.start_date.to_timestamp(), periods=len(p), freq='D')
        