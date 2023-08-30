import pandas as pd 

class TimeSeriesPreprocessor():
    def __init__(self, data, frequenct) -> None:
        self.data_df = data 
        self.frequency = frequenct

    def todatetime(self, timestamp):
        if str(timestamp).isdigit():
            if len(str(timestamp))==13:
                return pd.to_datetime(int(timestamp), unit='ms')
            elif len(str(timestamp))==19:
                return pd.to_datetime(int(timestamp), unit='ns')
        else:
            return pd.to_datetime(timestamp)

    def convert_and_set_time_index(self):
        self.data_df['time'] = self.data_df['time'].apply(self.todatetime)
        self.data_df = self.data_df.set_index('time') 

    def clean(self):
        self.data_df = self.data_df.dropna().drop_duplicates()
        self.data_df = self.data_df.sort_index()

    def run(self):
        self.clean()
        self.convert_and_set_time_index()
        return self.data_df

