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
