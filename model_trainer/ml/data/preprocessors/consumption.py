import pandas as pd 
import numpy as np 

from data.preprocessors.time_series import TimeSeriesPreprocessor

class ConsumptionPreProcessor(TimeSeriesPreprocessor):
    # Used for cummulative energy consumption data
    def __init__(self, data_df, frequency) -> None:
        self.data_df = data_df
        self.frequency = frequency

    def handle_missing_values(self):
        self.data_df = self.data_df.interpolate()

    def calculate_relative_consumption_from_total(self):
        def calc_diff(values):
            values = values.values
            
            if len(values) > 1:
                return values[-1] - values[0]
            if values:
                return values[0]
            return np.nan

        self.data_df = self.data_df.resample(self.frequency).agg(calc_diff)
    

    def run(self):
        self.clean()
        self.convert_and_set_time_index()
        self.calculate_relative_consumption_from_total()
        self.handle_missing_values()
        return self.data_df