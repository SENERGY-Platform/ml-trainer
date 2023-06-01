#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

echo $@

/wait_for_db.sh

python -m alembic upgrade head
pytest 

