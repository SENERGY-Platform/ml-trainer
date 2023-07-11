import uuid 

from flask import Blueprint, jsonify, request

from model_trainer.server.core.ray_handler import RayHandler
from model_trainer.server.core.mlflow_handler import MlflowHandler
from model_trainer.config import Config

config = Config()
train_blueprint = Blueprint("api", __name__)

@train_blueprint.route('/select', methods=['POST'])
def start_select():
    request_data = request.get_json()
    user_id = "user"
    models = request_data['models']
    task = request_data['task']
    model_artifact_name = request_data['model_artifact_name']
    data = request_data['kafka_topic_config']

    if 'experiment_name' not in request_data:
        experiment_name = str(uuid.uuid4().hex)
    else:
        experiment_name = request_data['experiment_name']

    mlflow_handler = MlflowHandler(config)
    experiment_can_be_used, reason = mlflow_handler.experiment_name_can_be_used(experiment_name)

    if not experiment_can_be_used:
        return jsonify({'error': reason})

    ray_handler = RayHandler(config)
    task_id = ray_handler.find_best_model(task, models, user_id, experiment_name, model_artifact_name, data)
    return jsonify({'task_id': str(task_id), 'status': 'Processing'})

@train_blueprint.route('/train/<job_id>', methods=['GET'])
def get_task_status(job_id):
    ray_handler = RayHandler(config)
    status, return_value = ray_handler.get_job_status(job_id)
    response = {'status': status}
    if return_value:
        response['response'] = return_value
    return jsonify(response)
    