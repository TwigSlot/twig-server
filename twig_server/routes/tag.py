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
from twig_server.routes.helper import helper_get_project, helper_get_resource, helper_get_tag, authorize_user, tag_belongs_to_project
def add_tag(project_id: str, resource_id: str):
    project = helper_get_project(project_id)

    tag_id = request.args.get("tag_uid")
    try:
        assert tag_id is not None
        tag_uid = int(tag_id)
    except:
        return "tag_uid is not an int", 404
    tag = Tag(current_app.config["driver"], uid = tag_uid)
    tag.query_uid()
    assert tag.db_obj is not None

    if(not authorize_user(project)):
        return "not authorized", 401

    if(not tag_belongs_to_project(tag, project)):
        return "resource not in project", 401
    
    resource_uid = int(resource_id)

    rls = Relationship(current_app.config['driver'], a_id=resource_uid, b_id=tag_uid)
    rls.query_endpoints()
    if('uid' in rls.properties):
        return "tag already attached to node", 404
    rls.create(Tag._label_resource_relationship)
    return jsonify(tag.properties)
    
def update_color(project_id: str, tag_id: str):
    project = helper_get_project(project_id)
    tag = helper_get_tag(tag_id)
    if(not authorize_user(project)):
        return "not authorized", 401
    if(not tag_belongs_to_project(tag, project)):
        return "tag does not belong to project", 401
    new_color = request.args.get("color")
    if(new_color is None):
        return "new color cannot be None", 404
    tag.set('color', new_color)
    tag.sync_properties()
    return jsonify(tag.properties)


def update_priority(project_id: str, tag_id: str):
    project = helper_get_project(project_id)
    tag = helper_get_tag(tag_id)
    if(not authorize_user(project)):
        return "not authorized", 401
    if(not tag_belongs_to_project(tag, project)):
        return "tag does not belong to project", 401
    new_priority = request.args.get("priority")
    if(new_priority is None):
        return "new priority cannot be None", 404
    tag.set('priority', int(new_priority))
    tag.sync_properties()
    return jsonify(tag.properties)
def update_name(project_id: str, tag_id: str):
    project = helper_get_project(project_id)
    tag = helper_get_tag(tag_id)
    if(not authorize_user(project)):
        return "not authorized", 401
    if(not tag_belongs_to_project(tag, project)):
        return "tag does not belong to project", 401
    new_name = request.args.get("name")
    if(new_name is None):
        return "new name cannot be None", 404
    tag.set('name', new_name)
    tag.sync_properties()
    return jsonify(tag.properties)


def get_tagged_resources(project_id: str, tag_id: str):
    project = helper_get_project(project_id)
    tag = helper_get_tag(tag_id)
    if(not tag_belongs_to_project(tag, project)):
        return "tag does not belong to project", 401
    resources = Resource.get_tagged_resources(current_app.config["driver"].conn, tag)
    ret = []
    for x in resources:
        col = x.get(x._Record__keys[0])
        assert type(col) is graph.Node
        ret.append(Node.extract_properties(col))    
    return jsonify(ret)

def create_tag(project_id: str):
    project = helper_get_project(project_id)
    if(not authorize_user(project)):
        return "not authorized", 401

    tag_name = request.args.get("name")
    tag_color = request.args.get("color")
    if(tag_color is None):
        tag_color = "pink"
    tag = Tag(current_app.config["driver"], name=tag_name)
    tag.create(project)
    tag.set("color", tag_color)
    tag.set("priority", 0)
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

def dissociate_tag(project_id: str, resource_id: str):
    tag_id = request.args.get("tag_uid")
    resource = helper_get_resource(resource_id)
    try:
        assert tag_id is not None
        tag_uid = int(tag_id)
    except:
        return "tag_uid is not an int", 404
    tag = Tag(current_app.config["driver"], uid= tag_uid)
    rls_properties = resource.find_rls_with(tag)
    rls = Relationship(current_app.config["driver"], uid = rls_properties['uid'])
    rls.query_uid()
    assert rls.db_obj is not None
    rls.delete()
    return "deleted", 200

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