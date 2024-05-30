from flask import Blueprint, jsonify, request, current_app

from model_trainer.ray_handler import RayKubeJobHandler
from model_trainer.kubernetes_client import KubernetesAPIClient
from model_trainer.config import Config

config = Config()
train_blueprint = Blueprint("api", __name__)

@train_blueprint.route('/job/<job_id>', methods=['GET'])
def get_task_status(job_id):
    k8s_client = KubernetesAPIClient()
    status, msg = k8s_client.get_job_status(job_id)
    response = {
        'success': status,
        'response': msg
    }
    return jsonify(response)
    
@train_blueprint.route('/loadshifting', methods=['POST'])
def loadshifting():
    user_id = "user"
    request_data = request.get_json()
    experiment_name = request_data['experiment_name'] 
    data_settings = request_data['data_settings']
    data_settings['file_name'] = experiment_name
    ray_image = request_data['ray_image']
    toolbox_version = request_data.get('toolbox_version', "v2.0.16")
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
    user_id = "user"
    request_data = request.get_json()
    experiment_name = request_data['experiment_name'] 
    data_settings = request_data['data_settings']
    task_settings = request_data['task_settings']
    ray_image = request_data['ray_image']
    toolbox_version = request_data.get('toolbox_version', "v2.0.16")
    task = "ml_fit"
    data_source = request_data['data_source']
    ray_handler = RayKubeJobHandler()
    try:
        task_id = ray_handler.start_job(task, task_settings, user_id, experiment_name, data_settings, ray_image, toolbox_version, data_source)
        return jsonify({'task_id': str(task_id), 'status': 'Processing'})
    except Exception as e:
        current_app.logger.error("Could not start job: " + str(e))
        return jsonify({'error': 'could not start job', 'message': str(e)})
