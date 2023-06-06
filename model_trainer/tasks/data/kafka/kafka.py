from ksql import KSQLAPI
import pandas as pd 

from config import KafkaTopicConfiguration

class KafkaLoader():
    def __init__(self, ksql_server_url, topic_config: KafkaTopicConfiguration):
       self.stream_name = "data10"
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
        flattened_time_path = self.build_flatten_string(self.topic_config.path_to_time)
        flattened_value_path = self.build_flatten_string(self.topic_config.path_to_value)

        query = f"""
        SELECT {flattened_time_path} as time, {flattened_value_path} as value
        FROM {self.stream_name}
        """

        #WHERE device_id == {self.topic_config.filterValue}
        print(query)
        return query

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
        value_string = self.build_column_string(self.topic_config.path_to_value)
        time_string = self.build_column_string(self.topic_config.path_to_time)

        query = f"""CREATE STREAM {self.stream_name} ({value_string}, {time_string})
        WITH (kafka_topic='{self.topic_config.name}', value_format='json', partitions=1);"""
        print(query)
        self.client.ksql(query)

    def load_data(self):
        self.create_stream()
        result_list = []

        try:
            result = self.client.query(self.build_select_query())
            result_list = [item for item in result]
        except Exception as e:
            print(type(e))
            print('Iteration done')
        self.data = self.convert_result_to_dataframe(result_list)
    
    def convert_result_to_dataframe(self, result):
        # Strip off first and last info messages
        result = result[1:-2]
        rows = []
        for row in result:
            print(row)
            values = row['row']['columns']
            time = values[0]
            value = values[1]
            rows.append({'time': time, 'value': value})
        df = pd.DataFrame(rows)
        print(df)
        return df

    def get_data(self):
        return self.data