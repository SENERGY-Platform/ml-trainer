from darts.datasets import AirPassengersDataset

class DummyLoader():
    def __init__(self):
        self.data = None

    def connect(self):
        pass

    def load_data(self):
        self.data = AirPassengersDataset().load()      

    def get_data(self):
        df = self.data.pd_dataframe()
        df = df.reset_index()
        df = df.rename(columns={"#Passengers": "value", "Month": "time"})
        return df
