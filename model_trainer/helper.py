import pytest
from model_trainer.server import app
from model_trainer.config import Config

@pytest.fixture()
def app():
    app.config.from_object(Config())
    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()