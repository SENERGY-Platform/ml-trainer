import uuid 
import json 

from model_trainer.kubernetes_client import KubernetesAPIClient
from model_trainer.config import Config

class RayKubeJobHandler():
    def __init__(self):
        self.k8sclient = KubernetesAPIClient()
    
    def start_load_shifting_job(self, user_id, experiment_name, data_settings, ray_image, toolbox_version):
        name = experiment_name + str(uuid.uuid4().hex)
        data_settings['file_name'] = experiment_name
        envs = {
            'TASK': "load_shifting",
            'USER_ID': user_id,
            'EXPERIMENT_NAME': name,
            'DATA_SETTINGS': json.dumps(data_settings),
            'DATA_SOURCE': "s3",
            'MLFLOW_URL': Config().MLFLOW_URL
        }
        self.k8sclient.create_job(envs, name, ray_image, toolbox_version)

