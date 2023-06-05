FROM python:3.9 AS builder

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

#RUN git log -1 --oneline > version.txt

WORKDIR /app
COPY model_trainer model_trainer

ENTRYPOINT ["/entrypoint"]

FROM builder AS api
WORKDIR /app
COPY ./build/start_api.sh /entrypoint
RUN chmod +x /entrypoint

FROM builder AS test 
ENV TESTING True
ENV DEBUG True
COPY ./build/run_tests.sh /entrypoint
RUN chmod +x /entrypoint
