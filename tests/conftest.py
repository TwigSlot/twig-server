import pytest
from dotenv import load_dotenv
from twig_server.app import create_app
from twig_server.database.connection import Neo4jConnection 
from flask import current_app
import os

if os.getenv("_PYTEST_RAISE", "0") != "0":
    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call):
        raise call.excinfo.value
    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo):
        raise excinfo.value

@pytest.fixture(scope = 'session', autouse = True)
def load_env():
    load_dotenv()

@pytest.fixture(scope='session')
def app():
    app = create_app({'TESTING':True})
    return app


@pytest.fixture(scope="session")
def connection(app):
    with app.app_context():
        assert current_app.driver != None
        yield current_app.driver
        current_app.driver.close()