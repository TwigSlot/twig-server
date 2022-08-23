import pytest
from dotenv import load_dotenv
from twig_server.app import create_app
from flask import current_app
import os

from twig_server.database.User import User

if (
    os.getenv("_PYTEST_RAISE", "0") != "0"
):  # for pytest debugging to work, do not execute in vscode! use launch.json instead

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call):
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo):
        raise excinfo.value


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture(scope="session")
def app():
    app = create_app({"TESTING": True})
    return app


@pytest.fixture(scope="session")
def connection(app):
    with app.app_context():
        assert current_app.config["driver"] != None
        yield current_app.config["driver"]
        current_app.config["driver"].close()


@pytest.fixture(scope="session")
def create_user_username(connection):
    jh = User(connection, username="jh")  # creating a user needs a username
    assert jh != None
    assert jh.db_obj == None
    db_obj = jh.create()
    assert db_obj != None
    assert jh.db_obj != None
    assert db_obj == jh.db_obj
    yield jh
    jh.delete()
