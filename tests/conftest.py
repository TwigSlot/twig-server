import os

import pytest
from dotenv import load_dotenv

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
def neo4j_server():
    from neo4j import GraphDatabase

    # TODO: Make this less hardcoded
    # TODO: This can't be parallelized!
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "notneo4j"))
    if driver.verify_connectivity():
        return driver
    else:
        raise RuntimeError("Cannot connect to neo4j server")