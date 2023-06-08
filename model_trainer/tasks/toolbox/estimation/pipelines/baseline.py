from darts.models import NaiveMean
import mlflow 

class Baseline(mlflow.pyfunc.PythonModel):
    def __init__(self, freq, add_time_covariates, **kwargs) -> None:
        super().__init__()
        
        self.model = NaiveMean()

    def fit(self, train_ts):
        self.model.fit(train_ts)
        
    def predict(self, number_steps):
        return self.model.predict(number_steps)