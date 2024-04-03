import os
import sys
print(f"Current working directory: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

import logging 

from flask import Flask, request, jsonify

from model_trainer.config import Config
from model_trainer.model_trainer.api import train_blueprint

def create_app():
    # instantiate the app
    app = Flask(__name__)

    # set config
    app.config.from_object(Config())

    # set logging to debug when debug is enabled, otherwise default to warning
    if Config.FLASK_DEBUG:
        app.logger.setLevel(logging.DEBUG)

    # register blueprints
    app.register_blueprint(train_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app}

    return app

app = create_app()

@app.before_request
def before():
    values = 'values: '
    if len(request.values) == 0:
        values += '(None)'
    for key in request.values:
        values += key + ': ' + request.values[key] + ', '
    app.logger.debug(values)

    if request.content_type == "application/json":
        app.logger.debug(f'data: {request.json}')

# Useful debugging interceptor to log all endpoint responses
@app.after_request
def after(response):
    app.logger.info(f"{request.remote_addr} - {request.method} - {request.scheme} - {request.full_path} - {response.status}")
    app.logger.debug('response: ' + response.status + ', ' + response.data.decode('utf-8'))
    return response

# Default handler for uncaught exceptions in the app
@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception.original_exception)
    if Config().FLASK_ENV != 'production':
        return jsonify({'error': str(exception.original_exception)}), 500
    return jsonify({'error': 'There was an unexpected error'}), 500

class APIError(Exception):
    """All custom API Exceptions"""
    pass

@app.errorhandler(APIError)
def handle_http_exception(e):
    app.logger.info('Bad request', e)
    return jsonify({'error': str(e)}), 400