from celery import Celery
from model_trainer.config import Config
import ray 
import mlflow 

#ray.init('localhost:4000')

config = Config()
mlflow.set_tracking_uri(config.MLFLOW_URL)
print(mlflow.get_artifact_uri())

app = Celery(
    'celery_app',
    include=['model_trainer.worker.tasks']
)

app.config_from_object(config)
