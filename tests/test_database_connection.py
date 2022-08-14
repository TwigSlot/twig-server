import pytest
from flask import current_app
import os


def test_env_vars():
    assert "NEO4J_SERVER_URL" in os.environ
    assert "NEO4J_USERNAME" in os.environ
    assert "NEO4J_PASSWORD" in os.environ

def test_app(app):
    assert app != None

def test_connection(connection):
    connection.verify_connectivity()

