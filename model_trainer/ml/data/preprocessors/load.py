from .consumption import ConsumptionPreProcessor
from .time_series import TimeSeriesPreprocessor

def get_preprocessor(processor_name):
    if processor_name == "diff":
        return ConsumptionPreProcessor
    else:
        return TimeSeriesPreprocessor