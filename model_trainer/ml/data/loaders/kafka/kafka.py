import uuid
import json 
from collections import defaultdict

from ksql import KSQLAPI
import pandas as pd 
from ksql_query_builder import Builder, SelectContainer, CreateContainer
from config import KafkaTopicConfiguration

class KafkaLoader():
    def __init__(self, ksql_server_url, topic_config: KafkaTopicConfiguration, experiment_name):
       self.stream_name = f'{experiment_name}{str(uuid.uuid4().hex)}'
       self.topic_config = topic_config
       self.ksql_server_url = ksql_server_url
       self.builder = Builder()

    def connect(self):
        self.client = KSQLAPI(self.ksql_server_url)
    
    def create_stream(self):
        create_containers = [
            CreateContainer(path=self.topic_config.path_to_time, type="STRING"), 
            CreateContainer(path=self.topic_config.path_to_value, type="DOUBLE"), 
            CreateContainer(path="device_id", type="STRING")
        ]
        query = self.builder.build_create_stream_query(self.stream_name, self.topic_config.name, create_containers)
        print(query)
        self.client.ksql(query)

    def load_data(self):
        self.create_stream()
        result_list = []

        select_containers = [
            SelectContainer(column_name="time", path=self.topic_config.path_to_time), 
            SelectContainer(column_name="value", path=self.topic_config.path_to_value)
        ]

        try:
            select_query = self.builder.build_select_query(self.stream_name, select_containers)
            select_query += f" WHERE {self.topic_config.filterType} = '{self.topic_config.filterValue}'"
            print(select_query)

            result = self.client.query(select_query)
            for item in result:
                result_list.append(item)    
        except Exception as e:
            print(e)
            print('Iteration done')
        
        data = self.clean_ksql_response(result_list)
        self.data = self.convert_result_to_dataframe(data)
        if self.data.empty:
            raise Exception("DataFrame is empty. Check the query.")

        drop_stream_query = f'DROP STREAM {self.stream_name}' 
        print(drop_stream_query)
        self.client.ksql(drop_stream_query)

    def clean_ksql_response(self, response):
        # Strip off first and last info messages
        data = []
        response = response[1:-1]
        for item in response:
            item = item.replace(",\n", "")
            item = json.loads(item)
            data.append(item)
        return data 

    def convert_result_to_dataframe(self, result):
        rows = []
        for row in result:
            values = row['row']['columns']
            time = values[0]
            value = values[1]
            rows.append({'time': time, 'value': value})
        df = pd.DataFrame(rows)
        return df

    def get_data(self):
        return self.data