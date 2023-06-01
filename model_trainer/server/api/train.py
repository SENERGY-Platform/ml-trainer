from flask import Blueprint, jsonify, request
from celery.result import AsyncResult

from model_trainer.server.core.tasks import get_job_status, select_job

train_blueprint = Blueprint("api", __name__)

@train_blueprint.route('/select', methods=['POST'])
def start_select():
    request_data = request.get_json()
    user_id = "user"
    models = request_data['models']
    task = request_data['task']
    model_artifact_name = request_data['model_artifact_name']
    experiment_name = request_data['experiment_name']
    task_id = select_job(task, models, user_id, experiment_name, model_artifact_name)
    return jsonify({'task_id': str(task_id), 'status': 'Processing'})

@train_blueprint.route('/train/<job_id>', methods=['GET'])
def get_task_status(job_id):
    status, return_value = get_job_status(job_id)
    response = {'status': status}
    if return_value:
        response['response'] = return_value
    return jsonify(response)
    