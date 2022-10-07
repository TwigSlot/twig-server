from flask import jsonify, current_app, request
from twig_server.database.Project import Project

from twig_server.database.User import User
from twig_server.database.Resource import Resource
from twig_server.database.native import Node, Relationship
from neo4j import graph

import twig_server.app as app

def explore():
    projects = Project.explore_projects(current_app.config['driver'].conn)
    ret: list = []
    owners = {}
    for x in projects:
        owner = Node.extract_properties(x.get(x._Record__keys[0]))['kratos_user_id']
        if(owner in owners): continue
        owner_user = User(current_app.config['driver'], kratos_user_id=owner)
        owner_user.query_kratos_user_id()
        owners[owner] = owner_user
    for x in projects:
        owner = Node.extract_properties(x.get(x._Record__keys[0]))['kratos_user_id']
        col = x.get(x._Record__keys[1])
        if(type(col) is graph.Node):
            # is a node
            ret.append({'project':Node.extract_properties(col), 'owner':owners[owner].properties})
    return jsonify({'projects':ret}), 200

def new_project():
    kratos_user_id = request.headers.get('X-User')
    debug = app.app.config['DEBUG']
    if(kratos_user_id is None and debug): # for dev
        kratos_user_id = request.args.get("user") 
    if(kratos_user_id is None):
        return "not authorized", 401
    assert kratos_user_id is not None
    user = User(current_app.config["driver"], kratos_user_id=kratos_user_id)
    user.query_kratos_user_id()
    assert user.db_obj is not None
    project = Project(current_app.config["driver"], owner=user)
    project.create(user)
    return jsonify({'project':project.properties, 'owner': user.properties}), 200


def list_resources(project: Project):
    resources = Resource.list_resources(
        current_app.config["driver"].conn, project
    )
    ret: list = []
    for x in resources:
        col = x.get(x._Record__keys[2])
        assert type(col) is graph.Node
        ret.append(Node.extract_properties(col))
    return ret


def list_relationships(project: Project):
    resources = Relationship.list_relationships(
        current_app.config["driver"].conn, project
    )
    ret: list = []
    for x in resources:
        row = []
        for i in range(len(x)):
            col = x.get(x._Record__keys[i])
            if type(col) is graph.Node:
                row.append(Node.extract_properties(col)["uid"])
            else:
                row.append(Relationship.extract_properties(col))
        ret.append(row)
    return ret


def edit_project(project_id: str):

    project = Project(current_app.config["driver"], uid=int(project_id))
    res = project.query_uid()
    if res is None:
        return "project not found", 404

    kratos_user_id = request.headers.get('X-User')
    owner = project.get_owner()
    if(kratos_user_id != owner['kratos_user_id']):
        return "not authorized", 401

    for key in request.args:
        value = request.args.get(key)
        project.set(key, value)
    return jsonify(project.properties), 200


def delete_project(project_id: str):
    project = Project(current_app.config["driver"], uid=int(project_id))

    kratos_user_id = request.headers.get('X-User')
    owner = project.get_owner()
    if(kratos_user_id != owner['kratos_user_id']):
        return "not authorized", 401

    res = project.query_uid()
    if res:
        project.delete()
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 404

def update_positions(project_id: str):
    p = Project(current_app.config['driver'], uid=project_id)
    pr = p.query_uid()
    kratos_user_id = request.headers.get('X-User')
    owner = p.get_owner()
    if(owner['kratos_user_id'] != kratos_user_id):
        return "not authorized", 401
    Resource.update_all_positions(
            current_app.config['driver'], request.json, project_id=int(project_id))
    return "ok", 200
def query_project(project_id: str):
    list_items: bool = False
    req_list_items = request.args.get("list_items")
    if (
        req_list_items is None
        or req_list_items.lower() != "true"
        or req_list_items != "1"
    ):
        list_items = True
    project = Project(current_app.config["driver"], uid=int(project_id))
    res = project.query_uid()
    if res:
        ans = []
        if list_items:
            ans = list_resources(project=project)
            ans2 = list_relationships(project=project)
            if ans2:
                ans.extend(ans2)
        return (
            jsonify(
                {
                    "project": project.properties,
                    "items": ans,
                    "user": str(request.headers),
                }
            ),
            200,
        )
    return "no such project", 404
