from flask import Flask, current_app, request

from twig_server.database.connection import Neo4jConnection
from twig_server.database.User import User

import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config.from_mapping(
    NEO4J_USERNAME=os.getenv("NEO4J_USERNAME"),
    NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD"),
    NEO4J_SERVER_URL=os.getenv("NEO4J_SERVER_URL"),
)
with app.app_context():
    current_app.config['driver'] = Neo4jConnection(  # TODO might be good to change this bad practice in future
        app.config.get("NEO4J_USERNAME"),
        app.config.get("NEO4J_PASSWORD"),
        app.config.get("NEO4J_SERVER_URL"),
    )
    current_app.config['driver'].connect()
    current_app.config['driver'].verify_connectivity()


@app.route("/")
def index():
    return "Index"


@app.route("/new/project", methods=["POST"])
def new_project():
    print(request.headers)


@app.route("/user/<kratos_username_or_user_id>", methods=["GET"])
def query_user(kratos_username_or_user_id: str):
    print(request.cookies)
    user = User(current_app.config['driver'], username=kratos_username_or_user_id)
    res = user.query_username()
    if res:
        return str(res._properties)

    user = User(current_app.config['driver'], kratos_user_id=kratos_username_or_user_id)
    res = user.query_kratos_user_id()
    if res:
        # todo: capture and deserialize the result of the query
        return str(res._properties)
    else:
        user.create()
        res = user.query_kratos_user_id()
        return str(res._properties)


def create_app(test_config=None):
    if test_config is not None:
        app.config.update(test_config)
    return app
