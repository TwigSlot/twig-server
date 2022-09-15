from flask import jsonify, current_app, request, redirect, url_for
from twig_server.database.Project import Project

from twig_server.database.User import User
from neo4j import graph

from twig_server.database.native import Node
import twig_server.app as app

def list_projects(user: User):
    projects = Project.list_projects(current_app.config['driver'].conn, user)
    ret: list = []
    for x in projects:
        col = x.get(x._Record__keys[2])
        owner = Node.extract_properties(x.get(x._Record__keys[0]))['kratos_user_id']
        if(type(col) is graph.Node):
            # is a node
            ret.append({
                'project':Node.extract_properties(col),
                'owner': owner
                })
    return ret

def concat_user_info_with_project_list(user: User):
    return jsonify({'user': user.properties, 'projects': list_projects(user)}), 200

def new_user(kratos_user_id: str):
    user = User(
        current_app.config["driver"], kratos_user_id=kratos_user_id
    )
    res = user.query_kratos_user_id()
    if res:
        return "user was already created", 200
    if(kratos_user_id == request.headers.get('X-User')):
        user.create()
        return concat_user_info_with_project_list(user)
    else:
        return "not authorized", 401
 
def query_user(kratos_username_or_user_id: str):
    user = User(
        current_app.config["driver"], kratos_user_id=kratos_username_or_user_id
    )
    res = user.query_kratos_user_id()
    if res:
        # todo: capture and deserialize the result of the query
        return concat_user_info_with_project_list(user)
    user = User(
        current_app.config["driver"], username=kratos_username_or_user_id
    )
    res = user.query_username()
    if res:
        return concat_user_info_with_project_list(user)
    else:
        return new_user(kratos_user_id=kratos_username_or_user_id)