from os import environ
import uuid 

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
    experiment_name: str = None

@dataclass
class EstimationSettings:
    frequency: str 

@dataclass
class AnomalySettings:
    frequency: str 
    window_size: int
    stride: int

class Config:
    """Base config."""
    KSQL_SERVER_URL = environ["KSQL_SERVER_URL"]
    MLFLOW_URL = environ['MLFLOW_URL']
    EXPERIMENT_NAME = environ.get('EXPERIMENT_NAME', str(uuid.uuid4().hex))
    MODEL_ARTIFACT_NAME = environ.get('MODEL_ARTIFACT_NAME')
    METRIC_FOR_SELECTION = environ.get('METRIC_FOR_SELECTION', 'mae')
    METRIC_DIRECTION = environ.get('METRIC_DIRECTION', 'min')
    USER_ID = environ['USER_ID']
    TASK = environ.get('TASK')
    COMMIT = environ['COMMIT']
    MODELS = environ.get('MODELS','').split(';')
    DATA_SOURCE = environ['DATA_SOURCE']
    PREPROCESSOR = environ.get('PREPROCESSOR')
    
    def __init__(self) -> None:
        self.parse_data_settings()
        if environ.get('TASK_SETTINGS'):
            self.parse_task_settings(environ.get('TASK_SETTINGS'))

    def parse_data_settings(self):
        if self.DATA_SOURCE == 'kafka':
            self.DATA_SETTINGS = KafkaTopicConfiguration(**json.loads(environ['DATA_SETTINGS']))
            
    def parse_task_settings(self, task_settings):
        task_settings = json.loads(task_settings)
        if self.TASK == "anomaly":
            self.TASK_SETTINGS = AnomalySettings(**task_settings)
        elif self.TASK == "estimation":
            self.TASK_SETTINGS = EstimationSettings(**task_settings)