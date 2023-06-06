from .kafka import KafkaLoader
from config import KafkaTopicConfiguration

data_config = KafkaTopicConfiguration()

def test_flatten_string(mocker):
    l = KafkaLoader(data_config)
    path = "value.energy.total"
    expected_flattened_string = "value->energy->total"
    actual_flattened_string = l.build_flatten_string(path)
    assert(expected_flattened_string == actual_flattened_string)

def test_column_string(mocker):
    l = KafkaLoader(data_config)
    path = "value.energy.total"
    expected_column_string = "value STRUCT<energy STRUCT<total DOUBLE>>"
    actual_column_string = l.build_column_string(path)
    assert(expected_column_string == actual_column_string)