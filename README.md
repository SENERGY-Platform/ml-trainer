# Model Trainer
This service is responsible for management of machine learning model training. At the moment it can start jobs, which will be started as an instance of the K8S CRD `RayJobs` as the compute infrastructure is based on Ray. The status of the job can also be retrieved via the K8S API.

# Usage
The web framework `FastAPI` is used which automatically generates Swagger documentation.
Run `make run_api` to start the server and browse to `http://localhost:5001/docs`. 
`Pydantic` is used to the schema validation.