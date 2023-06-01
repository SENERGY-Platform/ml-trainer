from darts.datasets import AirPassengersDataset

def load_est_data():
    return AirPassengersDataset().load()