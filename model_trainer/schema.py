from pydantic import BaseModel, HttpUrl, field_validator
from typing import Literal, Union, Any, Optional

class Kafka(BaseModel):
    name: str 
    path_to_time: str
    path_to_value: str
    filterType: Literal['device_id', 'operator_id', 'import_id']
    filterValue: str
    ksql_url: HttpUrl
    timestamp_format: str
    time_range_value: float
    time_range_level: str

class S3(BaseModel):
    s3_url: HttpUrl
    bucket_name: str 
    aws_secret: str 
    aws_access: str
    file_name: str
    
class Timescale(BaseModel):
    connection_string: Optional[str] = None
    device_id: str
    service_id: str
    field: str
    time_range: str = "1d"


class DummyDataSettings(BaseModel):
    pass
    
class ModelParameter(BaseModel):
    window_length: int
    batch_size: int
    lr: float
    num_epochs: int
    loss: str
    op: str
    latent_dims: int
    early_stopping_patience: int
    early_stopping_delta: float
    kernel_size: int

class MlFitSettings(BaseModel):
    model_name: Literal['cnn', 'trf']
    model_parameter: ModelParameter

class EmptyTaskSettings(BaseModel):
    pass

class Cluster(BaseModel):
    number_workers: Optional[int] = None
    cpu_worker_limit: Optional[int] = None
    memory_worker_limit: Optional[str] = None

class Job(BaseModel):
    task: Literal['anomaly_detection', 'load_shifting', 'peak_shaving']
    task_settings: Optional[MlFitSettings] = None
    data_source: Literal['kafka', 's3', 'dummy', 'timescale']
    data_settings: Union[Kafka, S3, Timescale, DummyDataSettings]
    toolbox_version: str
    ray_image: str
    ray_version: str
    user_id: str
    cluster: Cluster

    @field_validator('data_settings', mode='before')
    @classmethod
    def validate_data_settings_for_source(cls, value: Any, info):
        source = info.data.get('data_source')
        source_model_mapping = {
            'kafka': Kafka,
            's3': S3,
            'timescale': Timescale,
            'dummy': DummyDataSettings,
        }

        model = source_model_mapping.get(source)
        if model is None:
            return value
        if isinstance(value, model):
            return value
        return model.model_validate(value)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task": "anomaly_detection",
                    "task_settings": {
                        "model_parameter": {
                        "window_length": 205,
                        "batch_size": 1,
                        "lr": 0.0001,
                        "num_epochs": 20,
                        "loss": "MSE",
                        "op": "Adam",
                        "latent_dims": 32,
                        "early_stopping_patience": 0,
                        "early_stopping_delta": 0,
                        "kernel_size": 7
                    },
                    "model_name": "cnn"
                },
                "data_source": "kafka",
                "data_settings": {
                    "name": "topic",
                    "path_to_time": "value.energy.time",
                    "path_to_value": "value.energy.power",
                    "filterType": "device_id",
                    "filterValue": "urn:...",
                    "ksql_url": "http://ksql.kafka-sql:8088",
                    "timestamp_format": "unix", #yyyy-MM-ddTHH:mm:ss.SSSZ
                    "time_range_value": "13",
                    "time_range_level": "h"
                },
                "toolbox_version": "v2.2.92",
                "ray_image": "ghcr.io/senergy-platform/ray:v0.0.15",
                "ray_version": "2.53.0"
            }]
        }
    }
    

class JobStartResponse(BaseModel):
    task_id: str

class JobStartSuccessResponse(JobStartResponse):
    status: Literal['running']

class JobStatus(BaseModel):
    success: str 
    response: str
