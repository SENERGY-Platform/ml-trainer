#!/bin/bash

set -o errexit
set -o nounset

/wait_for_db.sh

celery -A model_trainer.worker.worker worker --loglevel=info