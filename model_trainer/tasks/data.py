from darts.datasets import AirPassengersDataset
from ksql import KSQLAPI
import os

class DataLoader():
    def __init__(self):
        self.data = None

    def load_data(self):
        self.data = AirPassengersDataset().load()      

    def get_data(self):
        return self.data

class KafkaLoader():
    def __init__(self, topic, mapping, filter):
       self.client = KSQLAPI(os.environ['KSQL_SERVER'])
       self.stream_name = "data"
       self.topic = topic
       self.mapping = mapping
       self.filter = filter

    def build_select_query(self):
        return f"select * from {self.stream_name}"

    def create_stream(self):
        query = f"""CREATE STREAM {self.stream_name} (profileId VARCHAR, latitude DOUBLE, longitude DOUBLE)
        WITH (kafka_topic='{self.topic}', value_format='json', partitions=1);"""

        self.client.query(query)

    def load_data(self):
        self.create_stream()
        self.client.query(self.build_select_query())