import uuid 
import json 
import base64

from model_trainer.kubernetes_client import KubernetesAPIClient
from model_trainer.config import Config

def generate_random_short_id():
    return base64.b32encode(uuid.uuid4().bytes).decode().replace("=","").lower()

class RayKubeJobHandler():
    def __init__(self):
        self.k8sclient = KubernetesAPIClient()
    
    def start_job(
        self, 
        task, 
        task_settings, 
        user_id, 
        experiment_name, 
        data_settings, 
        ray_image, 
        toolbox_version, 
        data_source,
        number_workers,
        ray_version,
        cpu_worker_limit
    ):
        name = experiment_name + generate_random_short_id() # Dont use `-` here as it results in errors with KSQL where the name is used as stream name
        envs = {
            'TASK': task,
            'TASK_SETTINGS': json.dumps(task_settings),
            'USER_ID': user_id,
            'EXPERIMENT_NAME': name,
            'DATA_SETTINGS': json.dumps(data_settings),
            'DATA_SOURCE': data_source,
            'MLFLOW_URL': Config().MLFLOW_URL,
            'TOOLBOX_VERSION': toolbox_version
        }
        self.k8sclient.create_job(envs, name, ray_image, toolbox_version, task, number_workers, ray_version, cpu_worker_limit)
        return name

