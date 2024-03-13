from .consumption import ConsumptionPreProcessor
from .time_series import TimeSeriesPreprocessor

def get_preprocessor(processor_name, data, frequency):
    if processor_name == "diff":
        return ConsumptionPreProcessor(data, frequency)
    else:
        return TimeSeriesPreprocessor(data, frequency)