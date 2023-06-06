from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base config."""
    FLASK_ENV = environ.get("FLASK_ENV", "production")
    FLASK_DEBUG = environ.get("FLASK_DEBUG", 'false') == 'true'
    TESTING = environ.get("TESTING", 'false') == 'true'
    MLFLOW_URL = environ['MLFLOW_URL'] 
    RAY_CLUSTER_URL = environ['RAY_CLUSTER_URL'] 
    TASK_WORKING_DIR = environ['TASK_WORKING_DIR']
    KSQL_SERVER_URL = environ['KSQL_SERVER_URL']

    
