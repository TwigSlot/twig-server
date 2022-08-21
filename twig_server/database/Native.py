# parent classes for 'native' neo4j objects: Nodes and Relationships
# mostly holds helper classes


from typing import Any, Mapping, Optional
from twig_server.database.connection import Neo4jConnection
from neo4j import Neo4jDriver, Result, Record


class Node:
    def __init__(self, conn: Neo4jConnection, uid: Optional[int] =None) -> None:
        """Initialize a new Node in Neo4J"""
        print("set properties")
        self.properties: Mapping[str, Any] = {}  # represents properties locally
        self.dbObj: Optional[ Record ] = None  
        # represents the data in the database

        self.properties["uid"] = uid
        self.db_conn: Neo4jDriver = conn.conn

        self.query_uid()  # try to retrieve existing database info for EXISTING UID

    # sync local properties with database data
    def sync_properties(self) -> None:
        self.properties = {}
        if self.dbObj == None:
            return  # if no response, properties will be empty
        assert self.dbObj is not None # for type checking
        self.properties["uid"] = int(self.dbObj.id)
        for key in self.dbObj._properties:
            self.properties[key] = self.dbObj[key]

    def query_uid(self, label_name: Optional[str] =None) -> Optional[Record]:
        if "uid" not in self.properties:  # querying for this UID
            return None
        queryStr = f"MATCH (n{(':'+label_name) if label_name else ''}) WHERE id(n)=$uid RETURN n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {"uid": self.properties["uid"]})
            self.dbObj = self.extract_node(res)
            self.sync_properties()
        return self.dbObj

    def delete(self) -> None: 
        if "uid" not in self.properties:
            raise Exception("No UID to delete")
        queryStr = f"MATCH (n) WHERE id(n)=$uid DETACH DELETE n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {"uid": self.properties["uid"]})
            self.dbObj = self.extract_node(res)

            self.sync_properties()

    def create(self, label_name: str) -> Record:
        if "uid" in self.properties:
            return self.dbObj
        queryStr = (
            f"CREATE (n{(':'+label_name) if label_name else ''}) RETURN n"
        )
        with self.db_conn.session() as session:
            res: Result = session.run(queryStr)
            self.dbObj = self.extract_node(res)
            self.sync_properties()
        return self.dbObj

    def extract_node(self, res: Result) -> Optional[Record]:
        """Pass in the row (Record) from a cypher query (Result)"""
        row = res.single()
        if row:
            row = row[0]
        else:
            return None
        return row

    def set(self, name: str, value: str) -> Optional[Record]:
        if "uid" not in self.properties:
            return None
        queryStr = (
            f"MATCH (n) WHERE id(n)=$uid SET n.`{name}` = $value RETURN n"
        )
        with self.db_conn.session() as session:
            res = session.run(
                queryStr,
                {"uid": self.properties["uid"], "name": name, "value": value},
            )
            self.dbObj = self.extract_node(res)
            self.sync_properties()
        return self.dbObj

    def get(self, name: str) -> Optional[str]:
        if name not in self.properties:
            return None
        return str(self.properties[name])


class Relationship:
    def __init__(
        self, conn: Neo4jConnection, **kwargs: Any
    ):  # uid = None, a_id = None, b_id = None):
        self.properties = {}
        self.properties["uid"] = 0
        # self.a_id = a_id
        # self.b_id = b_id
        # self.db_conn = conn.conn
        # self.query_uid()

    def extract_relationship(self, res: Result) -> Optional[Record]:
        row = res.single()
        if row:
            row = row[0]
        else:
            return None
        return row
