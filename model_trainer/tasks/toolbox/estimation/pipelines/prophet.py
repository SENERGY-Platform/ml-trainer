from darts.models import Prophet
from .helper import create_darts_encoder_based_on_freq
import mlflow 

class DartProphet(mlflow.pyfunc.PythonModel):
    def __init__(self, freq, add_time_covariates, **kwargs) -> None:
        super().__init__()

        if add_time_covariates:
            encoders = create_darts_encoder_based_on_freq(freq)
            kwargs['add_encoders'] = encoders

        self.model = Prophet(country_holidays="DE", **kwargs)
        # weekly and yearly seasonalities are automatically included in Prophet
        # https://facebook.github.io/prophet/docs/seasonality,_holiday_effects,_and_regressors.html

    def fit(self, train_ts):
        self.model.fit(train_ts)
        
    def predict(self, number_steps):
        return self.model.predict(number_steps)
    
    @staticmethod
    def get_hyperparams():
        # TODO depending on dataset freq 
        hyperparams = {
            "add_time_covariates": [True, False]
        }
        return hyperparams