from darts.datasets import AirPassengersDataset

from data.loaders.loader import DataLoader

class DummyLoader(DataLoader):
    def __init__(self):
        self.data = None

    def get_data(self):
        self.data = AirPassengersDataset().load()      
        df = self.data.pd_dataframe()
        df = df.reset_index()
        df = df.rename(columns={"#Passengers": "value", "Month": "time"})
        return df
