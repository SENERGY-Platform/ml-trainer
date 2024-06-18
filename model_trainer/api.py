from flask import Blueprint, jsonify, request, current_app

from model_trainer.ray_handler import RayKubeJobHandler
from model_trainer.kubernetes_client import KubernetesAPIClient
from model_trainer.config import Config
from model_trainer.exceptions import K8sException

config = Config()
train_blueprint = Blueprint("api", __name__)

def load_common_config_from_request():
    request_data = request.get_json()
    user_id = request_data.get("user_id", "unknown_user")
    experiment_name = request_data.get('experiment_name', "") 
    data_settings = request_data['data_settings']
    task_settings = request_data['task_settings']
    ray_image = request_data['ray_image']
    toolbox_version = request_data.get('toolbox_version', "v2.0.16")
    ray_version = request_data.get("ray_version", "2.0.9")
    return user_id, experiment_name, data_settings, task_settings, ray_image, toolbox_version, ray_version

def load_cluster_config():
    request_data = request.get_json()
    cluster = request_data.get("cluster", {})
    number_workers = cluster.get("number_workers", 1)
    cpu_worker_limit = cluster.get("cpu_worker_limit", 1)
    return number_workers, cpu_worker_limit

@train_blueprint.route('/job/<job_id>', methods=['GET'])
def get_task_status(job_id):
    k8s_client = KubernetesAPIClient()
    # TODO 404 when exception
    try:
        status, msg = k8s_client.get_job_status(job_id)
        response = {
            'success': status,
            'response': msg
        }
        return jsonify(response)
    except K8sException as e:
        response = {
            'response': e.body
        }
        return response, e.status

@train_blueprint.route('/loadshifting', methods=['POST'])
def loadshifting():
    user_id, experiment_name, data_settings, task_settings, ray_image, toolbox_version, ray_version = load_common_config_from_request()
    number_workers, cpu_worker_limit = load_cluster_config()
    data_settings['file_name'] = experiment_name
    data_source = 's3'
    task = "load_shifting"
    ray_handler = RayKubeJobHandler()
    try:
        task_id = ray_handler.start_job(task, None, user_id, experiment_name, data_settings, ray_image, toolbox_version, data_source, number_workers, ray_version, cpu_worker_limit)
        return jsonify({'task_id': str(task_id), 'status': 'Processing'})
    except Exception as e:
        current_app.logger.error("Could not start job: " + str(e))
        return jsonify({'error': 'could not start job', 'message': str(e)})

@train_blueprint.route('/mlfit', methods=['POST'])
def mlfit():
    user_id, experiment_name, data_settings, task_settings, ray_image, toolbox_version, ray_version = load_common_config_from_request()
    number_workers, cpu_worker_limit = load_cluster_config()
    request_data = request.get_json()
    data_source = request_data['data_source']
    task = request_data['task']
    ray_handler = RayKubeJobHandler()
    try:
        task_id = ray_handler.start_job(task, task_settings, user_id, experiment_name, data_settings, ray_image, toolbox_version, data_source, number_workers, ray_version, cpu_worker_limit)
        return jsonify({'task_id': str(task_id), 'status': 'Processing'})
    except Exception as e:
        current_app.logger.error("Could not start job: " + str(e))
        return jsonify({'error': 'could not start job', 'message': str(e)}), 500