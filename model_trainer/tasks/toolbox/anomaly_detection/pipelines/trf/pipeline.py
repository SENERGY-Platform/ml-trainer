from anomaly_detection.pipelines.custom_pipeline import AnomalyPipeline
from anomaly_detection.pipelines.trf.transformer import TransformerTimeSeriesEncoder

class TRFAnomalyPipeline(AnomalyPipeline):
    def __init__(self, config):
        super().__init__(config)

        self.model = TransformerTimeSeriesEncoder(number_encoder_layers=config["NUM_ENC_LAYERS"], 
                                                        number_heads=config["NUM_HEADS"], 
                                                        embedding_dimension=config["EMB_DIM"], 
                                                        sequence_length=config["SEQUENCE_LENGTH"], 
                                                        token_length=config["TOKEN_EMB_DIM"])

