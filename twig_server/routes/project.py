from flask import jsonify, current_app, request
from twig_server.database.Project import Project

from twig_server.database.connection import Neo4jConnection
from twig_server.database.User import User
from twig_server.database.Resource import Resource
from twig_server.database.native import Node, Relationship
from neo4j import graph

def new_project():
    kratos_user_id = request.args.get("user")
    assert kratos_user_id is not None
    user = User(current_app.config["driver"], kratos_user_id=kratos_user_id)
    user.query_kratos_user_id()
    assert user.db_obj is not None
    project = Project(current_app.config["driver"], owner=user)
    project.create(user)
    return project.properties

def list_resources(project: Project):
    resources = Resource.list_resources(current_app.config['driver'].conn, project)
    ret: list = []
    for x in resources:
        row = []
        for i in range(len(x)):
            col = x.get(x._Record__keys[i])
            if(type(col) is graph.Node):
                row.append(Node.extract_properties(col))
            else:
                row.append(Relationship.extract_properties(col))
        ret.append(row)
    return ret   

def edit_project(project_id: str):
    project = Project(current_app.config["driver"], uid=int(project_id))
    res = project.query_uid()
    if res is None:
        return "project not found", 404
    for key in request.args:
        value = request.args.get(key)
        project.set(key, value)
    return project.properties

def delete_project(project_id: str):
    project = Project(current_app.config["driver"], uid=int(project_id))
    res = project.query_uid()
    if(res):
        project.delete()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 404
def query_project(project_id: str):
    project = Project(current_app.config['driver'], uid = int(project_id))
    res = project.query_uid()
    if res:
        return list_resources(project=project)
    return 'no such project'

