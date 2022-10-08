import resource
from flask import jsonify, current_app, request
from twig_server.database.Project import Project
from twig_server.database.Tag import Tag

from twig_server.database.connection import Neo4jConnection
from twig_server.database.User import User
from twig_server.database.Resource import Resource
from neo4j import graph

from twig_server.database.native import Node, Relationship
import twig_server.app as app
from twig_server.routes.helper import helper_get_project, helper_get_resource, helper_get_tag, tag_belongs_to_project, authorize_user

def new_node(project):
    resource = Resource(current_app.config['driver'])
    resource.create(project)
    return jsonify(resource.properties)

def new_relationship(project, a_id: str, b_id: str):
    resource = Relationship(current_app.config['driver'], a_id=a_id, b_id=b_id)
    resource.create('prereq')
    return jsonify(resource.properties)

def new_item(project_id: str):
    project = helper_get_project(project_id)

    if(not authorize_user(project)):
        return "not authorized", 401

    if(request.args.get('item') == 'node'):
        return new_node(project), 200
    elif(request.args.get('item') == 'relationship'):
        a_id = request.args.get('a_id')
        b_id = request.args.get('b_id')
        assert a_id is not None
        assert b_id is not None
        return new_relationship(project, a_id, b_id), 200
    else:
        return "item must be set", 404
    
def edit_resource(project_id: str, resource_id: str):
    project = helper_get_project(project_id)
    resource = helper_get_resource(resource_id)
    res = resource.query_uid()
    if(not authorize_user(project)):
        return "not authorized", 401

    if res is None:
        return "resource not found", 404
    for key in request.args:
        value = request.args.get(key)
        resource.set(key, value)
    return jsonify(resource.properties), 200

def delete_resource(project_id: str, resource_id: str):
    project = helper_get_project(project_id)
    resource = helper_get_resource(resource_id)
    res = resource.query_uid()
    if(not authorize_user(project)):
        return "not authorized", 401

    if(res):
        resource.delete()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 404

def delete_relationship(project_id: str, relationship_id: str):
    project = helper_get_project(project_id)
    if(not authorize_user(project)):
        return "not authorized", 401

    relationship_uid= int(relationship_id)
    rls = Relationship(current_app.config["driver"], uid=relationship_uid)
    res = rls.query_uid()
    if res is not None:
        rls.delete()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 404

def edit_relationship(project_id: str, relationship_id: str):
    # not of great importance now
    return 'not implemented yet', 404