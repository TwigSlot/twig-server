import neo4j
from flask import Flask

from twig_server.neo4j import neo4j_driver

app = Flask(__name__)
app.config["NEO4J_DRIVER"]: neo4j.GraphDatabase = neo4j_driver


# /:username -> MATCH (n:User) WHERE n.username = username RETURN n

@app.route('/')
def index():
    return "Index"


@app.route("/query/<username>")
def query_user(username: str):
    query_stmt = "MATCH (n:User) WHERE n.username = $username  RETURN n"

    res = neo4j_driver.session().run(query_stmt, {"username": username})
    # todo: capture and deserialize the result of the query
    return query_stmt


def create_app():
    from dotenv import load_dotenv
    load_dotenv()
    return app
