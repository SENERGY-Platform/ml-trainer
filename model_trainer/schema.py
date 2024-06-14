from typing import Literal

class KafkaSettings():
    name: str 
    path_to_time: str
    path_to_value: str 
    filterType: Literal['device_id', 'operator_id', 'import_id']
    filterValue: str
    ksql_url: str 
    timestamp_format: str
    time_range_value: float
    time_range_level: str

class Job():
    data_source: Literal['kafka', 's3']
    data_settings: KafkaSettings
    toolbox_version: str
    ray_image: str 