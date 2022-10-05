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

def helper_get_project(project_id: str):
    project_uid = int(project_id)
    assert project_uid is not None
    project = Project(current_app.config["driver"], uid=project_uid)
    project.query_uid()
    assert project.db_obj is not None
    return project
def helper_get_resource(resource_id: str):
    resource_uid = int(resource_id)
    assert resource_uid is not None
    resource = Resource(current_app.config["driver"], uid=resource_uid)
    res = resource.query_uid()
    assert resource.db_obj is not None
    return resource

def authorize_user(project: Project):
    kratos_user_id = request.headers.get('X-User')
    owner = project.get_owner()
    if(kratos_user_id != owner['kratos_user_id']):
        return False
    return True

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

def add_tag(project_id: str, resource_id: str):
    project = helper_get_project(project_id)
    resource = helper_get_resource(resource_id)

    tag_id = request.args.get("tag_uid")
    try:
        assert tag_id is not None
        tag_uid = int(tag_id)
    except:
        return "tag_uid is not an int", 404
    tag = Tag(current_app.config["driver"], uid= tag_uid)
    tag.query_uid()
    app.app.logger.info(tag.properties)
    assert tag.db_obj is not None

    if(not authorize_user(project)):
        return "not authorized", 401

    if(int(resource.get_project().properties['uid']) != int(project_id)):
        return "resource not in project", 401
    
    resource_uid = int(resource_id)

    rls = Relationship(current_app.config['driver'], a_id=resource_uid, b_id=tag_uid)
    rls.query_endpoints()
    if('uid' in rls.properties):
        return "tag already attached to node", 404
    rls.create(Tag._label_resource_relationship)
    return jsonify(tag.properties)
    

def create_tag(project_id: str):
    project = helper_get_project(project_id)
    if(not authorize_user(project)):
        return "not authorized", 401

    tag_name = request.args.get("name")
    tag = Tag(current_app.config["driver"], name=tag_name)
    tag.create(project)
    return jsonify(tag.properties)

def list_tags(project_id: str, resource_id: str):
    resource = helper_get_resource(resource_id)
    tags = Resource.list_resource_tags(current_app.config["driver"].conn, resource)
    ret = []
    for x in tags:
        col = x.get(x._Record__keys[2])
        assert type(col) is graph.Node
        ret.append(Node.extract_properties(col))    
    return jsonify(ret)


def list_all_tags(project_id: str):
    project = helper_get_project(project_id)
    tags = Tag.list_project_tags(current_app.config["driver"].conn, project)
    ret = []
    for x in tags:
        col = x.get(x._Record__keys[2])
        assert type(col) is graph.Node
        ret.append(Node.extract_properties(col))    
    return jsonify(ret)

def delete_tag(project_id: str):
    project = helper_get_project(project_id)
    if(not authorize_user(project)):
        return "not authorized", 401
    tag_id = request.args.get('uid')
    tag = Tag(current_app.config["driver"], uid=tag_id)
    tag_db_obj = tag.query_uid()
    if(tag_db_obj):
        tag.delete()
        return "ok", 200
    else:
        return "tag not found", 404