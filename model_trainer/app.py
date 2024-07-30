import os
import sys
print(f"Current working directory: {os.getcwd()}")
print(f"Sys Path: {sys.path}")
import time
import json 
import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from model_trainer.logger import init_logger, logger
from model_trainer.ray_handler import RayKubeJobHandler
from model_trainer.kubernetes_client import KubernetesAPIClient
from model_trainer.config import Config
from model_trainer.exceptions import K8sException
from model_trainer.schema import Job, JobStartSuccessResponse, JobStatus


log_level = "info"
if Config().DEBUG:
    log_level = "debug"
init_logger(log_level)
app = FastAPI()

@app.middleware("http")
async def log(request: Request, call_next):
    start_time = time.time()
    body = ""
    if Config().DEBUG:
        body = await request.body()

    response = await call_next(request)
    process_time = time.time() - start_time
    log = {
        "method": str(request.method),
        "url": str(request.url),
        "headers": str(request.headers),
        "remote_client": str(request.client),
        "time": str(process_time),
        "response_code": response.status_code,
        "body": str(body)
    }

    logger.info(json.dumps(log))
    return response

@app.exception_handler(Exception)
def internal_error(request: Request, exc: Exception):    
    error = "".join(
                traceback.format_exception(
                    etype=type(exc), value=exc, tb=exc.__traceback__
                )
    )
    log = {
        "method": str(request.method),
        "url": str(request.url),
        "headers": str(request.headers),
        "remote_client": str(request.client),
        "error": error
    }

    logger.error(json.dumps(log))
    return JSONResponse(status_code=500, content={"error": error})

@app.get('/job/{job_id}', response_class=JSONResponse)
def get_job_status(job_id) -> JobStatus:
    k8s_client = KubernetesAPIClient()
    try:
        status, msg = k8s_client.get_job_status(job_id)
        response = {
            'success': status,
            'response': msg
        }
        return response
    except K8sException as e:
        response = {
            'sucess': 'error',
            'response': f"Original Satus Code: {e.status}: {e.response}"
        }
        raise HTTPException(status_code=e.status, detail=response)

@app.post('/job', response_class=JSONResponse)
def start_job(job: Job) -> JobStartSuccessResponse:
    ray_handler = RayKubeJobHandler()
    task_id = ray_handler.start_job(job)
    return {'task_id': str(task_id), 'status': 'running'}