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

COPY . .
RUN git log -1 --oneline > version.txt

ENTRYPOINT ["/entrypoint"]

FROM python:3.8.16-alpine3.18 AS api
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN adduser app --disabled-password
USER app

COPY --from=builder /opt/venv /opt/venv
COPY ./build/start_api.sh /entrypoint
COPY --from=builder /app/model_trainer /app/
COPY --from=builder /app/version.txt /app/ 
HEALTHCHECK CMD curl --fail http://localhost:5000 || exit 1

USER root
RUN chmod u+x /entrypoint
USER app

FROM builder AS test 
ENV TESTING True
ENV DEBUG True
COPY ./build/run_tests.sh /entrypoint
RUN chmod +x /entrypoint
