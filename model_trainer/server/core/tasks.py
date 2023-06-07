import json 
import os
from os.path import join as pjoin

from ray.job_submission import JobSubmissionClient, JobStatus
from model_trainer.config import Config

config = Config()
client = JobSubmissionClient(config.RAY_CLUSTER_URL)

def start_job(task, user_id, experiment_name, model_artifcat_name, envs):
    env_vars = {
        "MLFLOW_URL": config.MLFLOW_URL,
        "TASK": task,
        "USER_ID": user_id,
        "EXPERIMENT_NAME": experiment_name,
        "MODEL_ARTIFACT_NAME": model_artifcat_name
    }
    env_vars.update(envs)
    job_id = client.submit_job(
            # Entrypoint shell command to execute
            entrypoint="python select_best_model.py",
            # Path to the local directory that contains the script.py file
            runtime_env={
                "working_dir": config.TASK_WORKING_DIR, 

                # openssl>22.1.0 for ksql error module 'lib' has no attribute 'OpenSSL_add_all_algorithms'
                "pip": ["mlflow", "darts", "cryptography==38.0.4", "ksql"], 
                "env_vars": env_vars
            }
    )
    return job_id

def select_job(task, models, user_id, experiment_name, model_artifcat_name, data):
    envs = {"MODELS": ';'.join(models), 'KAFKA_TOPIC_CONFIG': json.dumps(data), 'KSQL_SERVER_URL': config.KSQL_SERVER_URL}
    return start_job(task, user_id, experiment_name, model_artifcat_name, envs)

def get_job_status(job_id):
    status = client.get_job_status(job_id)
    result = None
    if status == JobStatus.SUCCEEDED:
        logs = client.get_job_logs(job_id)
        result = logs.split('RESULT_START')[1]
        result = result.split('RESULT_END')[0]
        result = json.loads(result)
    return status, result