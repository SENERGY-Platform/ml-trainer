from ksql import KSQLAPI
from config import KafkaTopicConfiguration

class KafkaLoader():
    def __init__(self, ksql_server_url, topic_config: KafkaTopicConfiguration):
       self.stream_name = "data"
       self.topic_config = topic_config
       self.ksql_server_url = ksql_server_url

    def connect(self):
        self.client = KSQLAPI(self.ksql_server_url)

    def build_flatten_string(self, access_path):
        string = ""
        access_paths = access_path.split('.')
        for i, level in enumerate(access_paths):
            string += level

            if i < len(access_paths)-1:
                string += '->'
        return string

    def build_select_query(self):
        flattened_time_path = self.build_flatten_string()
        flattened_value_path = self.build_flatten_string()

        return f"""
        SELECT {flattened_time_path} as time, {flattened_value_path} as value, device_id
        FROM {self.stream_name}
        WHERE device_id == {self.topic_config.filterValue}
        """

    def build_column_string(self, access_path):
        string = ""
        access_paths = access_path.split('.')
        for i, level in enumerate(access_paths):
            string += level

            if i < len(access_paths)-1:
                string += ' STRUCT<'

        string += " DOUBLE"
        
        for _ in range(len(access_paths)-1):
            string += ">"

        return string

    def create_stream(self):
        value_string = self.build_column_string()
        time_string = self.build_column_string()

        query = f"""CREATE STREAM {self.stream_name} ({value_string}, {time_string})
        WITH (kafka_topic='{self.topic_config.name}', value_format='json', partitions=1);"""

        self.client.query(query)

    def load_data(self):
        self.create_stream()
        self.client.query(self.build_select_query())