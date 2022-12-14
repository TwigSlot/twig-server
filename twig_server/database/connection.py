import os
from typing import Optional

from neo4j import GraphDatabase, Neo4jDriver
import twig_server.app as app

class Neo4jConnection:
    def __init__(self, username: str, password: str, url: str) -> None:
        self.username: str = username
        self.password: str = password
        self.url: str = url
        self.conn: Optional[Neo4jDriver] = None

    def connect(self) -> None:
        self.conn = GraphDatabase.driver(
            self.url, auth=(self.username, self.password)
        )

    def verify_connectivity(self):
        self.conn.verify_connectivity()

    def close(self):
        self.conn.close()
