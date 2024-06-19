import threading 
import time 
from urllib.parse import urljoin
import mlflow 
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

class Downloader(threading.Thread):
    def __init__(
        self, 
        logger,
        model_ref,
        mlflow_url,
        ml_trainer_url,
        check_interval_seconds=60,
    ):
        threading.Thread.__init__(self)
        self.logger = logger 
        self.check_interval_seconds = check_interval_seconds
        self.model_ref = model_ref
        self.ml_trainer_url = ml_trainer_url
        self.__stop = True
        self.client = TrainerClient(ml_trainer_url, logger)
        mlflow.set_tracking_uri(mlflow_url)

    def run(self):
        self.logger.info("Start Downloader Thread")
        while not self.__stop:
            self.check()
            self.wait()

    def wait(self):
        time.sleep(self.check_interval_seconds)

    def check(self):
        if not self.job_id:
            self.logger.debug(f"Job ID missing")
            return 

        if not self.client.is_job_ready(self.job_id):
            self.logger.debug(f"Job {self.job_id} not ready yet")
            return

        model_uri = f"models:/{self.job_id}@production"
        self.logger.debug(f"Try to download model {self.job_id}")
        model = mlflow.pyfunc.load_model(model_uri)
        self.logger.debug(f"Downloading model {self.job_id} was succesfull")
        self.model_ref = model
        self.stop()

    def stop(self):
        self.logger.info("Stop Downloader Loop")
        self.__stop = True

    def start_loop(self, job_id):
        self.logger.info("Start Downloader Loop")
        self.job_id = job_id
        self.__stop = False



