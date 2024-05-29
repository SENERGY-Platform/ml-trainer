import uuid 
import json 

from model_trainer.kubernetes_client import KubernetesAPIClient
from model_trainer.config import Config

class RayKubeJobHandler():
    def __init__(self):
        self.k8sclient = KubernetesAPIClient()
    
    def start_job(self, task, task_settings, user_id, experiment_name, data_settings, ray_image, toolbox_version, data_source):
        name = experiment_name + str(uuid.uuid4().hex) # Dont use `-` here as it results in errors with KSQL where the name is used as stream name
        envs = {
            'TASK': task,
            'TASK_SETTINGS': json.dumps(task_settings),
            'USER_ID': user_id,
            'EXPERIMENT_NAME': name,
            'DATA_SETTINGS': json.dumps(data_settings),
            'DATA_SOURCE': data_source,
            'MLFLOW_URL': Config().MLFLOW_URL
        }
        self.k8sclient.create_job(envs, name, ray_image, toolbox_version)
        return name

