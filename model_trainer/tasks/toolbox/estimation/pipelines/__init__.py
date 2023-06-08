from .linear_reg import LinearReg
from .prophet import DartProphet
from .nhits import DartNHITS
from .baseline import Baseline

MODELS = [
    DartProphet, LinearReg, DartNHITS, Baseline
]