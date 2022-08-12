import neo4j
from flask import Flask

from twig_server.neo4j import neo4j_driver
from twig_server.database.User import Node, User

app = Flask(__name__)
app.config["NEO4J_DRIVER"]: neo4j.GraphDatabase = neo4j_driver


# /:username -> MATCH (n:User) WHERE n.username = username RETURN n

@app.route('/')
def index():
    return "Index"


@app.route("/query/<username>")
def query_user(username: str):
    user = User(username)
    res = user.query_username()
    if(res):
    # todo: capture and deserialize the result of the query
        return res._properties['username']
    else:
        res = user.create()
        return 'created user ' + res._properties['username']


def create_app():
    from dotenv import load_dotenv
    load_dotenv()
    return app
