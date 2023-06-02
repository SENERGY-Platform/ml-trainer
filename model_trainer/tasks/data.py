from darts.datasets import AirPassengersDataset
from ksql import KSQLAPI
import os
import json

class DataLoader():
    def __init__(self):
        self.data = None

    def load_data(self):
        self.data = AirPassengersDataset().load()      

    def get_data(self):
        return self.data

class KafkaLoader():
    def __init__(self, topic, mappings, inputTopics):
       self.client = KSQLAPI(os.environ['KSQL_SERVER'])
       self.stream_name = "data"
       self.topic = topic
       self.mappings = json.loads(mappings)
       self.inputTopics = json.loads(inputTopics)

    def build_select_query(self):
        return f"select time, value from {self.stream_name}"

    def create_stream(self):
        query = f"""CREATE STREAM {self.stream_name} (latitude DOUBLE)
        WITH (kafka_topic='{self.topic}', value_format='json', partitions=1);"""

        self.client.query(query)

    def load_data(self):
        self.create_stream()
        self.client.query(self.build_select_query())