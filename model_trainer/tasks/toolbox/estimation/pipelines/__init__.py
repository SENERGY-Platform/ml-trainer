from .linear_reg import LinearReg
from .prophet import DartProphet
from .baseline import Baseline
from .deepar import DeepAR
from .nhits import DartNHITS

MODELS = [
    DartProphet, LinearReg, DartNHITS
]