from darts.models import NHiTSModel
from .helper import create_darts_encoder_based_on_freq

class DartNHITS():
    def __init__(self, freq, add_time_covariates, **kwargs) -> None:
        if add_time_covariates:
            encoders = create_darts_encoder_based_on_freq(freq)
            kwargs['add_encoders'] = encoders

        self.model = NHiTSModel(num_stacks=3, num_blocks=2, num_layers=1, **kwargs)

        
    def fit(self, train_ts):
        self.model.fit(train_ts)
        
    def predict(self, number_steps):
        return self.model.predict(number_steps)

    @staticmethod
    def get_hyperparams():
        # TODO depending on dataset freq 
        hyperparams = {
            "add_time_covariates": [True, False],
            "output_chunk_length": [1],
            "input_chunk_length": [1,10,50]
        }
        return hyperparams
 