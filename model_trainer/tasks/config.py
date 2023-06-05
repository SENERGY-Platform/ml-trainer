from os import environ

from dataclasses import dataclass
import typing 
import json

@dataclass
class Mapping():
    dest: str = None
    source: str = None

@dataclass
class KafkaTopicConfiguration:
    """"""
    name: str = None
    filterType: str = None
    filterValue: str = None
    mappings: typing.List[Mapping] = None

    def __post_init__(self):
        self.mappings = [Mapping(m) for m in self.mappings]

class Config:
    """Base config."""
    KSQL_SERVER = environ.get("KSQL_SERVER", "https://localhost:8088")
    MLFLOW_URL = environ['MLFLOW_URL']
    MODELS = environ['MODELS']
    EXPERIMENT_NAME = environ['EXPERIMENT_NAME']
    MODEL_ARTIFACT_NAME = environ['MODEL_ARTIFACT_NAME']
    METRIC_FOR_SELECTION = environ.get('METRIC_FOR_SELECTION', 'mae')
    METRIC_DIRECTION = environ.get('METRIC_DIRECTION', 'min')
    USER_ID = environ['USER_ID']
    TASK = environ['TASK']
    KAFKA_TOPIC_CONFIG = environ['KAFKA_TOPIC_CONFIG']

    def __init__(self):
        self.MODELS = self.MODELS.split(';')

        topic_config = json.loads(self.KAFKA_TOPIC_CONFIG)
        self.KAFKA_TOPIC_CONFIG = KafkaTopicConfiguration(**topic_config)