import os
from typing import Optional

from neo4j import GraphDatabase, Neo4jDriver

neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_SERVER_URL"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
)


class Neo4jConnection:
    def __init__(self):
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.url = os.getenv("NEO4J_SERVER_URL")
        self.conn: Optional[Neo4jDriver] = None

    def connect(self) -> None:
        self.conn = GraphDatabase.driver(
            self.url, auth=(self.username, self.password)
        )
