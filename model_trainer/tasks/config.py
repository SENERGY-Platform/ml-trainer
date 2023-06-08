from os import environ

from dataclasses import dataclass
import typing 
import json

@dataclass
class KafkaTopicConfiguration:
    """"""
    name: str = None
    filterType: str = None
    filterValue: str = None
    path_to_time: str = None
    path_to_value: str = None


class Config:
    """Base config."""
    KSQL_SERVER_URL = environ["KSQL_SERVER_URL"]
    MLFLOW_URL = environ['MLFLOW_URL']
    MODELS = environ['MODELS']
    EXPERIMENT_NAME = environ['EXPERIMENT_NAME']
    MODEL_ARTIFACT_NAME = environ['MODEL_ARTIFACT_NAME']
    METRIC_FOR_SELECTION = environ.get('METRIC_FOR_SELECTION', 'mae')
    METRIC_DIRECTION = environ.get('METRIC_DIRECTION', 'min')
    USER_ID = environ['USER_ID']
    TASK = environ['TASK']
    KAFKA_TOPIC_CONFIG = environ['KAFKA_TOPIC_CONFIG']
    COMMIT = environ['COMMIT']

    def __init__(self):
        self.MODELS = self.MODELS.split(';')

        topic_config = json.loads(self.KAFKA_TOPIC_CONFIG)
        self.KAFKA_TOPIC_CONFIG = KafkaTopicConfiguration(**topic_config)