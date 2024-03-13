from data.loaders.kafka.kafka import KafkaLoader
from data.loaders.dummy import DummyLoader
from config import Config

def get_data_loader(name, data_settings):
    if name == "kafka":
        config = Config()
        experiment_name = config.EXPERIMENT_NAME
        return KafkaLoader(config.KSQL_SERVER_URL, data_settings, experiment_name)
    elif name == "dummy":
        return DummyLoader()