import os

import pytest
from dotenv import load_dotenv


def pytest_configure(config: pytest.Config):
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
):
    integration_only = config.getoption("--integration")
    skip_integration = pytest.mark.skip(reason="running only unit tests")
    skip_non_integration = pytest.mark.skip(
        reason="running only integration tests"
    )
    for item in items:
        if (
            "integration_tests" in str(item.path)
            or "integration" in item.keywords
        ):
            if not integration_only:
                item.add_marker(skip_integration)
        else:
            if integration_only:
                item.add_marker(skip_non_integration)


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests ONLY",
    )


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
    driver = GraphDatabase.driver(
        "bolt://localhost:7687", auth=("neo4j", "notneo4j")
    )
    if driver.verify_connectivity():
        return driver
    else:
        raise RuntimeError("Cannot connect to neo4j server")
