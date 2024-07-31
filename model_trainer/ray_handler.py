import uuid 
import json 

from model_trainer.kubernetes_client import KubernetesAPIClient
from model_trainer.config import Config
from model_trainer.schema import Job 

def generate_random_short_id():
    return uuid.uuid4().hex

class RayKubeJobHandler():
    def __init__(self):
        self.k8sclient = KubernetesAPIClient()
    
    def start_job(
        self, 
        job: Job
    ):
        name = generate_random_short_id()
        envs = {
            'TASK': job.task,
            'USER_ID': job.user_id,
            'EXPERIMENT_NAME': name,
            'DATA_SETTINGS': job.data_settings.json(),
            'DATA_SOURCE': job.data_source,
            'MLFLOW_URL': Config().MLFLOW_URL,
            'TOOLBOX_VERSION': job.toolbox_version
        }
        if job.task_settings:
            envs['TASK_SETTINGS'] = job.task_settings.json()
        self.k8sclient.create_job(envs, name, job)
        return name

