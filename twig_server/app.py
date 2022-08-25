from flask import Flask, current_app
from twig_server.routes import misc, project, resource, user

import os
from dotenv import load_dotenv

from twig_server.database.connection import Neo4jConnection

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
        # TODO might be good to change this bad practice in future
    ] = Neo4jConnection(
        app.config.get("NEO4J_USERNAME"),
        app.config.get("NEO4J_PASSWORD"),
        app.config.get("NEO4J_SERVER_URL"),
    )
    current_app.config["driver"].connect()
    current_app.config["driver"].verify_connectivity()


@app.route("/")
def index():
    return "Index"


app.add_url_rule("/project/new", 
                 methods=["GET", "PUT"], view_func=project.new_project)
app.add_url_rule("/project/<project_id>",
                 methods=["GET"], view_func=project.query_project)
app.add_url_rule("/project/<project_id>/new",
                 methods=["GET", "PUT"], view_func=resource.new_resource)
app.add_url_rule("/user/<kratos_username_or_user_id>",
                 methods=["GET"], view_func=user.query_user)


def create_app(test_config=None):
    if test_config is not None:
        app.config.update(test_config)
    return app
