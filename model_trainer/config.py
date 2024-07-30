from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base config."""
    DEBUG = environ.get("DEBUG", 'true') == 'true' or environ.get("DEBUG", 'true') == 'True'
    MLFLOW_URL = environ['MLFLOW_URL'] 
