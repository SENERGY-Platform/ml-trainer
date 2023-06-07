from .linear_reg import LinearReg
from .prophet import DartProphet
from .nhits import DartNHITS

MODELS = [
    DartProphet, LinearReg, DartNHITS
]