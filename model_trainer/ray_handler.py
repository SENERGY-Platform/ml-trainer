import json 
import uuid 

from model_trainer.kubernetes_client import KubernetesAPIClient

class RayKubeJobHandler():
    def __init__(self):
        self.k8sclient = KubernetesAPIClient()
    
    def start_load_shifting_job(self, experiment_name, user_id, data_settings, ray_image):
        name = experiment_name + str(uuid.uuid4().hex)
        envs = {
            'TASK': "load_shifting",
            'USER': user_id,
            'EXPERIMENT_NAME': name,
            'DATA_SETTINGS': data_settings,
            'DATA_SOURCE': "s3"
        }
        self.k8sclient.create_job(envs, name, ray_image)

