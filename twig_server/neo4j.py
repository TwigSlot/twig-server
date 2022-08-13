import os
from neo4j import GraphDatabase

neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_SERVER_URL"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
)
