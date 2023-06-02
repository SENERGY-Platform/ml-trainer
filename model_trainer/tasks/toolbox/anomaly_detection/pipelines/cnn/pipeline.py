from anomaly_detection.pipelines.custom_pipeline import AnomalyPipeline
from anomaly_detection.pipelines.cnn.cnn_autoencoder import Autoencoder

class TRFAnomalyPipeline(AnomalyPipeline):
    def __init__(self, config):
        super().__init__(config)
        self.model = Autoencoder(config['LATENT_DIMS'])