import json 

from ray.job_submission import JobSubmissionClient, JobStatus

from model_trainer.versioning import get_commit

class RayHandler():
    def __init__(self, config):
        self.config = config
        self.client = JobSubmissionClient(config.RAY_CLUSTER_URL)

    def start_job(self, task, user_id, experiment_name, model_artifcat_name, additional_envs):
        env_vars = {
            "MLFLOW_URL": self.config.MLFLOW_URL,
            "TASK": task,
            "USER_ID": user_id,
            "EXPERIMENT_NAME": experiment_name,
            "MODEL_ARTIFACT_NAME": model_artifcat_name,
            "COMMIT": get_commit(self.config.PATH_COMMIT_VERSION)
        }
        env_vars.update(additional_envs)

        job_id = self.client.submit_job(
                # Entrypoint shell command to execute
                entrypoint="python select_best_model.py",
                # Path to the local directory that contains the script.py file
                runtime_env={
                    "working_dir": self.config.TASK_WORKING_DIR, 

                    # TODO changes are not applied on running cluster??
                    # cryptography for ksql error module 'lib' has no attribute 'OpenSSL_add_all_algorithms'
                    "pip": ["mlflow==2.4.0", "darts==0.24.0", "cryptography==38.0.4", "ksql", "git+https://github.com/SENERGY-Platform/ksql-query-builder"], 

                    # Pin pip and python version to find the packages specified above 
                    "pip_version": "==22.0.4;python_version=='3.8.16'",
                    "env_vars": env_vars,
                },

                # Run entrypoint script on a node with >2 CPUS so that Head Node (1 CPU) does not get jobs
                entrypoint_num_cpus=2
        )
        return job_id

    def get_job_status(self, job_id):
        status = self.client.get_job_status(job_id)
        result = None
        if status == JobStatus.SUCCEEDED:
            logs = self.client.get_job_logs(job_id)
            result = logs.split('RESULT_START')[1]
            result = result.split('RESULT_END')[0]
            result = json.loads(result)
        return status, result

    def find_best_model(self, task, models, user_id, experiment_name, model_artifcat_name, data):
        envs = {"MODELS": ';'.join(models), 'KAFKA_TOPIC_CONFIG': json.dumps(data), 'KSQL_SERVER_URL': self.config.KSQL_SERVER_URL}
        return self.start_job(task, user_id, experiment_name, model_artifcat_name, envs)


