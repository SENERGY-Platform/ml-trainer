#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

echo $@

/wait_for_db.sh

if [ $@ = "migrate" ]
then

else
    if [ $@ = "migrate_and_start" ]
    then
      gunicorn --bind 0.0.0.0:5000 app:app

    else
      gunicorn --bind 0.0.0.0:5000 app:app
    fi
fi

