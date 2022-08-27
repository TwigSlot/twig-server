from flask import jsonify, current_app, request
from twig_server.database.Project import Project

from twig_server.database.connection import Neo4jConnection
from twig_server.database.User import User
from twig_server.database.Resource import Resource
from neo4j import graph

from twig_server.database.native import Node
def list_projects(user: User):
    projects = Project.list_projects(current_app.config['driver'].conn, user)
    ret: list = []
    for x in projects:
        col = x.get(x._Record__keys[2])
        if(type(col) is graph.Node):
            # is a node
            ret.append(Node.extract_properties(col))
    return ret

def concat_user_info_with_project_list(user: User):
    return jsonify({'user': user.properties, 'projects': list_projects(user)}), 200
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
        user.create()
        res = user.query_kratos_user_id()
        return concat_user_info_with_project_list(user)

