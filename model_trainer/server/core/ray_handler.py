import json 

from ray.job_submission import JobSubmissionClient, JobStatus

from model_trainer.versioning import get_commit

class RayHandler():
    def __init__(self, config):
        self.config = config
        self.client = JobSubmissionClient(config.RAY_CLUSTER_URL)

    def start_job(self, user_id, experiment_name, additional_envs, entrypoint_file):
        env_vars = {
            "MLFLOW_URL": self.config.MLFLOW_URL,
            "USER_ID": user_id,
            "EXPERIMENT_NAME": experiment_name,
            "COMMIT": get_commit(self.config.PATH_COMMIT_VERSION)
        }
        env_vars.update(additional_envs)

        job_id = self.client.submit_job(
                # Entrypoint shell command to execute
                entrypoint=f"python {entrypoint_file}.py",
                # Path to the local directory that contains the script.py file
                runtime_env={
                    "working_dir": self.config.TASK_WORKING_DIR, 

                    # environments are only recreate when something changes, with out version, it will not load the latest version
                    # cryptography for ksql error module 'lib' has no attribute 'OpenSSL_add_all_algorithms'
                    "pip": [
                        "mlflow==2.5.0", 
                        "darts==0.24.0", 
                        "cryptography==38.0.4", 
                        "ksql==0.10.2", 
                        "git+https://github.com/SENERGY-Platform/ksql-query-builder",
                        "git+https://github.com/SENERGY-Platform/timeseries-toolbox@v1.16",
                        "python-dotenv==1.0.0",
                    ], 

                    # Pin pip and python version to find the packages specified above 
                    "pip_version": "==22.0.4;python_version=='3.8.16'",
                    "env_vars": env_vars,

                    # exclude .env in the task directory as it shall only be used for local testing
                    "excludes": [".env"]
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

    def find_best_model(
        self, 
        task, 
        models, 
        user_id, 
        experiment_name, 
        model_artifcat_name, 
        data, 
        task_settings, 
        data_source, 
        preprocessor_name,
        metric_for_selection
    ):
        envs = {
            "MODELS": ';'.join(models), 
            'DATA_SETTINGS': json.dumps(data), 
            'DATA_SOURCE': data_source,
            'KSQL_SERVER_URL': self.config.KSQL_SERVER_URL,
            "TASK_SETTINGS": json.dumps(task_settings),
            "PREPROCESSOR": preprocessor_name,
            "METRIC_FOR_SELECTION": metric_for_selection,
            "TASK": task,
            "MODEL_ARTIFACT_NAME": model_artifcat_name,
        }
        return self.start_job(user_id, experiment_name, envs, 'select_best_model')


