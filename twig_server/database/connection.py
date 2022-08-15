import os
from typing import Optional

from neo4j import GraphDatabase, Neo4jDriver


class Neo4jConnection:
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url
        self.conn: Optional[Neo4jDriver] = None

    def connect(self) -> None:
        self.conn = GraphDatabase.driver(
            self.url, auth=(self.username, self.password)
        )

    def verify_connectivity(self):
        self.conn.verify_connectivity()

    def close(self):
        self.conn.close()
