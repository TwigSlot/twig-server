from flask import Flask, current_app

from twig_server.database.connection import Neo4jConnection
from twig_server.database.User import User

import os

app = Flask(__name__)


@app.route("/")
def index():
    return "Index"


@app.route("/query/<username>")
def query_user(username: str):
    user = User(username)
    res = user.query_username()
    if res:
        # todo: capture and deserialize the result of the query
        return res._properties["username"]
    else:
        res = user.create()
        return "created user " + res._properties["username"]


def create_app(test_config: dict = None):
    from dotenv import load_dotenv

    load_dotenv()

    app.config.from_mapping(
        NEO4J_USERNAME=os.getenv("NEO4J_USERNAME"),
        NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD"),
        NEO4J_SERVER_URL=os.getenv("NEO4J_SERVER_URL"),
    )
    if test_config is not None:
        app.config.update(test_config)
    with app.app_context():
        current_app.driver = Neo4jConnection(
            # TODO might be good to change this bad practice in future
            app.config.get("NEO4J_USERNAME"),
            app.config.get("NEO4J_PASSWORD"),
            app.config.get("NEO4J_SERVER_URL"),
        )
        current_app.driver.connect()
        current_app.driver.verify_connectivity()

    return app
