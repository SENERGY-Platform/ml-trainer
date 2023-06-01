# API
The API container serves as the main API if a training shall be started. Each request will start a training in one of the workers. It can be polled for the status of the training.

# Worker
Each worker runs one or multiple trainings and pushes a serialized version of the model (either pickle or ONNX) to the Model Repository.

# Flower
UI to manage jobs

# Redis
A redis db is used as job queue where the Trainer API pushes new jobs and worker nodes pick up jobs.