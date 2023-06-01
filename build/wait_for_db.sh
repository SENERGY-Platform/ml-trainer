#!/bin/bash

postgres_ready() {
python << END
import sys

import psycopg2
import urllib.parse as urlparse
import os

try:
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    dbname = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
except Exception as e:
    print(e)
    sys.exit(-1)
sys.exit(0)

END
}

until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

#exec "$@"