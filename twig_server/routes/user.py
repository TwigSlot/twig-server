from flask import Flask, current_app, request
from twig_server.database.Project import Project

from twig_server.database.connection import Neo4jConnection
from twig_server.database.User import User
from twig_server.database.Resource import Resource
from neo4j import graph

def list_projects(user: User):
    projects = Project.list_projects(current_app.config['driver'].conn, user)
    ret: list = []
    for x in projects:
        row = []
        for i in range(len(x)):
            col = x.get(x._Record__keys[i])
            if(type(col) is graph.Node):
                # is a node
                row.append(col._properties)
            else:
                # is a relationship
                row.append(col._properties)
        ret.append(row)
        
    return str(ret)
def query_user(kratos_username_or_user_id: str):
    user = User(
        current_app.config["driver"], username=kratos_username_or_user_id
    )
    res = user.query_username()
    if res:
        return list_projects(user)

    user = User(
        current_app.config["driver"], kratos_user_id=kratos_username_or_user_id
    )
    res = user.query_kratos_user_id()
    if res:
        # todo: capture and deserialize the result of the query
        return list_projects(user)
    else:
        user.create()
        res = user.query_kratos_user_id()
        return list_projects(user)

