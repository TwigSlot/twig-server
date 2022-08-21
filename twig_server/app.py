from flask import Flask, current_app, request
from twig_server.database.Project import Project

from twig_server.database.connection import Neo4jConnection
from twig_server.database.User import User
from neo4j import graph

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
    current_app.config[
        "driver"
    ] = Neo4jConnection(  # TODO might be good to change this bad practice in future
        app.config.get("NEO4J_USERNAME"),
        app.config.get("NEO4J_PASSWORD"),
        app.config.get("NEO4J_SERVER_URL"),
    )
    current_app.config["driver"].connect()
    current_app.config["driver"].verify_connectivity()


@app.route("/")
def index():
    return "Index"


@app.route("/new/project", methods=["GET", "POST"])
def new_project():
    kratos_user_id = request.args.get("user")
    user = User(current_app.config["driver"], kratos_user_id=kratos_user_id)
    user.query_kratos_user_id()
    res = Project(current_app.config["driver"], owner=user).create(user)
    return res._properties

def list_projects(user: User):
    projects = Project.list_projects(current_app.config['driver'].conn, user)
    ret: list = []
    for x in projects:
        row = []
        for i in range(len(x)):
            col = x.get(x._Record__keys[i])
            if(type(col) is graph.Node):
                # is a node
                row.append(col._properties)
            else:
                # is a relationship
                row.append(col._properties)
        ret.append(row)
        
    return str(ret)

@app.route("/user/<kratos_username_or_user_id>", methods=["GET"])
def query_user(kratos_username_or_user_id: str):
    print(request.cookies)
    user = User(
        current_app.config["driver"], username=kratos_username_or_user_id
    )
    res = user.query_username()
    if res:
        return list_projects(user)

    user = User(
        current_app.config["driver"], kratos_user_id=kratos_username_or_user_id
    )
    res = user.query_kratos_user_id()
    if res:
        # todo: capture and deserialize the result of the query
        return list_projects(user)
    else:
        user.create()
        res = user.query_kratos_user_id()
        return list_projects(user)


def create_app(test_config=None):
    if test_config is not None:
        app.config.update(test_config)
    return app
