from darts.models import LinearRegressionModel
import mlflow 

from .helper import create_darts_encoder_based_on_freq

class LinearReg(mlflow.pyfunc.PythonModel):
    def __init__(self, freq, add_time_covariates, **kwargs) -> None:
        super().__init__()
        
        if add_time_covariates:
            encoders = create_darts_encoder_based_on_freq(freq)
            kwargs['add_encoders'] = encoders

        if add_time_covariates:
            kwargs['lags_future_covariates'] = (0, kwargs['lags'])

        self.model = LinearRegressionModel(**kwargs)

    def fit(self, train_ts):
        self.model.fit(train_ts)
        
    def predict(self, number_steps):
        return self.model.predict(number_steps)

    @staticmethod
    def get_hyperparams():
        # TODO depending on dataset freq 
        hyperparams = {
            "add_time_covariates": [True],
            "lags": [1, 10]
        }
        return hyperparams