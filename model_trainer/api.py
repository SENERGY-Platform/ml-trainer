import uuid 

from flask import Blueprint, jsonify, request, current_app

from model_trainer.ray_handler import RayKubeJobHandler
from model_trainer.mlflow_handler import MlflowHandler
from model_trainer.config import Config

config = Config()
train_blueprint = Blueprint("api", __name__)

#@train_blueprint.route('/select', methods=['POST'])
#def start_select():
#    request_data = request.get_json()
#    user_id = "user"
#    models = request_data['models']
#    task = request_data['task']
#    model_artifact_name = request_data['model_artifact_name']
#    data_settings = request_data['data_settings']
#    data_source = request_data['data_source']
#    task_settings = request_data['task_settings']
#    preprocessor_name = request_data['preprocessor']
#    metric_for_selection = request_data['selection_metric']

#    if 'experiment_name' not in request_data:
#        experiment_name = str(uuid.uuid4().hex)
#    else:
#        experiment_name = request_data['experiment_name']

#    mlflow_handler = MlflowHandler(config)
#    experiment_can_be_used, reason = mlflow_handler.experiment_name_can_be_used(experiment_name)

#    if not experiment_can_be_used:
#        return jsonify({'error': reason})

#    return jsonify({'task_id': str("task_id"), 'status': 'Processing'})

#@train_blueprint.route('/train/<job_id>', methods=['GET'])
#def get_task_status(job_id):
#    ray_handler = RayHandler(config)
#    status, return_value = ray_handler.get_job_status(job_id)
#    response = {'status': status}
#    if return_value:
#        response['response'] = return_value
#    return jsonify(response)
    
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