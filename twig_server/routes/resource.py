from flask import Flask, current_app, request
from twig_server.database.Project import Project

from twig_server.database.connection import Neo4jConnection
from twig_server.database.User import User
from twig_server.database.Resource import Resource
from neo4j import graph

from twig_server.database.native import Relationship

def new_node(project) -> str:
    resource = Resource(current_app.config['driver'])
    resource.create(project)
    return resource.properties

def new_relationship(project, a_id: str, b_id: str):
    resource = Relationship(current_app.config['driver'], a_id=a_id, b_id=b_id)
    resource.create('prereq')
    return resource.properties

def new_item(project_id: str):
    project_uid = int(project_id)
    assert project_uid is not None
    project = Project(current_app.config["driver"], uid=project_uid)
    project.query_uid()
    assert project.db_obj is not None
    if(request.args.get('item') == 'node'):
        return new_node(project)
    elif(request.args.get('item') == 'relationship'):
        a_id = request.args.get('a_id')
        b_id = request.args.get('b_id')
        assert a_id is not None
        assert b_id is not None
        return new_relationship(project, a_id, b_id)
    else:
        return "item must be set", 404
    
def edit_resource(project_id: str, resource_id: str):
    project_uid = int(project_id)
    assert project_uid is not None
    project = Project(current_app.config["driver"], uid=project_uid)
    project.query_uid()
    assert project.db_obj is not None

    resource_uid = int(resource_id)
    assert resource_uid is not None
    resource = Resource(current_app.config["driver"], uid=resource_uid)
    res = resource.query_uid()
    assert resource.db_obj is not None

    # TODO check resource owner == project

    if res is None:
        return "resource not found", 404
    for key in request.args:
        value = request.args.get(key)
        resource.set(key, value)
    return resource.properties