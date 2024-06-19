from urllib.parse import urljoin
import requests

class TrainerClient():
    def __init__(self, url, logger) -> None:
        self.url = url 
        self.logger = logger

    def is_job_ready(self, job_id):
        status_url = urljoin(self.url, 'job', job_id)
        res = requests.get(status_url)
        if res.status_code != 200:
            raise Exception(f"Cant get job status: {res.text}")
        res_data = res.json()
        job_status = res_data['success'] 
        self.logger.debug(f"Training Job Status: {job_status}")
        if job_status == 'error':
            raise Exception(f"Error occured inside Job: {res_data['response']}")

        return job_status == 'done'

    def start_training(self, job_request, endpoint):
        self.logger.debug(f"Start online training")
        train_url = urljoin(self.url, endpoint)
        res = requests.post(train_url, json=job_request)
        self.logger.debug(f"ML Trainer Response: {res.text}")
        if res.status_code != 200:
            raise Exception(f"Cant start training job {res.text}")
        job_id = res.json()['task_id']
        return job_id



