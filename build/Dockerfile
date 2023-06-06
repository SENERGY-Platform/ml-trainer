FROM python:3.8.16 AS builder

WORKDIR /app
RUN apt-get -y install libc-dev libssl-dev

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

# problem with ksql RUN python3 -m pip install -U pip

# Requirements are installed here to ensure they will be cached.
COPY requirements.txt .
RUN python3 -m pip install -Ur requirements.txt

COPY .git .git
RUN git log -1 --oneline > version.txt

FROM python:3.8.16-slim-bullseye AS api

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

# make entrypoint executable as root
COPY ./build/start_api.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN adduser app --disabled-password
USER app

COPY --from=builder /opt/venv /opt/venv
COPY model_trainer /app/model_trainer
COPY --from=builder /app/version.txt /app/ 
HEALTHCHECK CMD curl --fail http://localhost:5000 || exit 1
ENTRYPOINT ["sh", "/app/entrypoint.sh"]

FROM builder AS test 
ENV TESTING True
ENV DEBUG True
COPY ./build/run_tests.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["sh", "/entrypoint.sh"]

