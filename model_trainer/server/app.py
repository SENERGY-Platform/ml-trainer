import logging 

from flask import Flask

from model_trainer.config import Config
from model_trainer.server.api.train import train_blueprint

def create_app():
    # instantiate the app
    app = Flask(__name__)

    # set config
    app.config.from_object(Config())

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