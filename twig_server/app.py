from flask import Flask, current_app
from flask_cors import CORS
from twig_server.routes import misc, project, resource, user

import os
from dotenv import load_dotenv

from twig_server.database.connection import Neo4jConnection

load_dotenv()
app = Flask(__name__)
CORS(app)
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
                 methods=["PUT"], view_func=project.new_project)
app.add_url_rule("/project/<project_id>",
                 methods=["GET"], view_func=project.query_project)
app.add_url_rule("/project/<project_id>/edit",
                 methods=["POST", "PATCH"], view_func=project.edit_project)
app.add_url_rule("/project/<project_id>/delete", 
                 methods=["POST", "DELETE"], view_func=project.delete_project)
app.add_url_rule("/project/<project_id>/positions/update",
                 methods=["POST"], view_func=project.update_positions)
app.add_url_rule("/project/<project_id>/new",
                 methods=["POST", "PUT"], view_func=resource.new_item)

app.add_url_rule("/project/<project_id>/resource/<resource_id>/add_tag",
                 methods=["POST", "PUT"], view_func=resource.add_tag)
app.add_url_rule("/project/<project_id>/resource/<resource_id>/list_tags",
                 methods=["GET"], view_func=resource.list_tags)
app.add_url_rule("/project/<project_id>/resource/<resource_id>/dissociate_tag",
                 methods=["POST", "DELETE"], view_func=resource.dissociate_tag)
app.add_url_rule("/project/<project_id>/create_tag",
                 methods=["POST", "PUT"], view_func=resource.create_tag)
app.add_url_rule("/project/<project_id>/list_all_tags",
                 methods=["GET"], view_func=resource.list_all_tags)
app.add_url_rule("/project/<project_id>/delete_tag",
                 methods=["POST", "DELETE"], view_func=resource.delete_tag)

app.add_url_rule("/project/<project_id>/resource/<resource_id>/edit",
                 methods=["POST", "PUT"], view_func=resource.edit_resource)
app.add_url_rule("/project/<project_id>/resource/<resource_id>/delete",
                 methods=["POST", "DELETE"], view_func=resource.delete_resource)
app.add_url_rule("/project/<project_id>/relationship/<relationship_id>/edit",
                 methods=["POST", "PUT"], view_func=resource.edit_relationship)
app.add_url_rule("/project/<project_id>/relationship/<relationship_id>/delete",
                 methods=["POST", "DELETE"], view_func=resource.delete_relationship)

app.add_url_rule("/user/<kratos_username_or_user_id>",
                 methods=["GET"], view_func=user.query_user)
app.add_url_rule("/user/<kratos_user_id>",
                 methods=["PUT"], view_func=user.new_user)
app.add_url_rule("/explore",
                 methods=["GET"], view_func=project.explore)
app.add_url_rule("/user/update/<kratos_user_id>",
                 methods=["POST"], view_func=user.update_user)

def create_app(test_config=None):
    if test_config is not None:
        app.config.update(test_config)
    return app
