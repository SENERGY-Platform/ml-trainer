import json 

from model_trainer.worker.tasks.train_anomaly_detector import train_anomaly_detector
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
                "pip": ["mlflow", "darts"],
                "env_vars": env_vars
            }
    )
    return job_id

def select_job(task, models, user_id, experiment_name, model_artifcat_name):
    envs = {"MODELS": ';'.join(models)}
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