from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base config."""
    FLASK_ENV = environ.get("FLASK_ENV", "production")
    FLASK_DEBUG = environ.get("FLASK_DEBUG", 'false') == 'true'
    TESTING = environ.get("TESTING", 'false') == 'true'
    MLFLOW_URL = environ.get('MLFLOW_URL', "localhost") 
    RAY_CLUSTER_URL = environ.get('RAY_CLUSTER_URL', 'localhost:4000') 
    TASK_WORKING_DIR = environ.get('TASK_WORKING_DIR', './model_trainer/tasks')

    
