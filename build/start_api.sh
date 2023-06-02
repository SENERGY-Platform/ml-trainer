#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

gunicorn --bind 0.0.0.0:5000 model_trainer/server/app:app
