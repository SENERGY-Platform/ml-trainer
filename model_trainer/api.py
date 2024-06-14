from flask import Blueprint, jsonify, request, current_app

from model_trainer.ray_handler import RayKubeJobHandler
from model_trainer.kubernetes_client import KubernetesAPIClient
from model_trainer.config import Config
from model_trainer.exceptions import K8sException

config = Config()
train_blueprint = Blueprint("api", __name__)

def load_common_config_from_request():
    request_data = request.get_json()
    user_id = request_data("unknown_user")
    experiment_name = request_data.get('experiment_name', "") 
    data_settings = request_data['data_settings']
    task_settings = request_data['task_settings']
    ray_image = request_data['ray_image']
    toolbox_version = request_data.get('toolbox_version', "v2.0.16")
    return user_id, experiment_name, data_settings, task_settings, ray_image, toolbox_version

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
    user_id, experiment_name, data_settings, task_settings, ray_image, toolbox_version = load_common_config_from_request()
    data_settings['file_name'] = experiment_name
    data_source = 's3'
    task = "load_shifting"
    ray_handler = RayKubeJobHandler()
    try:
        task_id = ray_handler.start_job(task, None, user_id, experiment_name, data_settings, ray_image, toolbox_version, data_source)
        return jsonify({'task_id': str(task_id), 'status': 'Processing'})
    except Exception as e:
        current_app.logger.error("Could not start job: " + str(e))
        return jsonify({'error': 'could not start job', 'message': str(e)})

@train_blueprint.route('/mlfit', methods=['POST'])
def anomaly():
    user_id, experiment_name, data_settings, task_settings, ray_image, toolbox_version = load_common_config_from_request()
    request_data = request.get_json()
    task = "ml_fit"
    data_source = request_data['data_source']
    ray_handler = RayKubeJobHandler()
    try:
        task_id = ray_handler.start_job(task, task_settings, user_id, experiment_name, data_settings, ray_image, toolbox_version, data_source)
        return jsonify({'task_id': str(task_id), 'status': 'Processing'})
    except Exception as e:
        current_app.logger.error("Could not start job: " + str(e))
        return jsonify({'error': 'could not start job', 'message': str(e)}), 500

@train_blueprint.route('/peak_shaving', methods=['POST'])
def anomaly():
    user_id, experiment_name, data_settings, task_settings, ray_image, toolbox_version = load_common_config_from_request()
    request_data = request.get_json()
    task = "peak_shaving"
    data_source = request_data['data_source']
    ray_handler = RayKubeJobHandler()
    try:
        task_id = ray_handler.start_job(task, task_settings, user_id, experiment_name, data_settings, ray_image, toolbox_version, data_source)
        return jsonify({'task_id': str(task_id), 'status': 'Processing'})
    except Exception as e:
        current_app.logger.error("Could not start job: " + str(e))
        return jsonify({'error': 'could not start job', 'message': str(e)}), 500
