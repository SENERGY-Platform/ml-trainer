from os import environ
from dotenv import load_dotenv

load_dotenv()
from dataclasses import dataclass
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
    EXPERIMENT_NAME = environ['EXPERIMENT_NAME']
    MODEL_ARTIFACT_NAME = environ['MODEL_ARTIFACT_NAME']
    METRIC_FOR_SELECTION = environ.get('METRIC_FOR_SELECTION', 'mae')
    METRIC_DIRECTION = environ.get('METRIC_DIRECTION', 'min')
    USER_ID = environ['USER_ID']
    TASK = environ['TASK']
    COMMIT = environ['COMMIT']
    MODELS = environ['MODELS'].split(';')
    KAFKA_TOPIC_CONFIG = KafkaTopicConfiguration(**json.loads(environ['KAFKA_TOPIC_CONFIG']))