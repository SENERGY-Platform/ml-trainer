FROM python:3.9 AS builder

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Additional dependencies
  && apt-get install -y telnet netcat \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

#RUN git log -1 --oneline > version.txt

WORKDIR /app
COPY model_trainer model_trainer
COPY app.py app.py
COPY ./build/wait_for_db.sh /wait_for_db.sh
RUN chmod +x /wait_for_db.sh

ENTRYPOINT ["/entrypoint"]

FROM builder AS api
WORKDIR /app
COPY ./build/start_api.sh /entrypoint
RUN chmod +x /entrypoint

FROM builder AS worker
WORKDIR /app
COPY ./build/start_worker.sh /entrypoint
RUN chmod +x /entrypoint

FROM builder AS test 
ENV TESTING True
ENV DEBUG True
COPY ./build/run_tests.sh /entrypoint
RUN chmod +x /entrypoint
