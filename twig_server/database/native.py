# parent classes for 'native' neo4j objects: Nodes and Relationships
# mostly holds helper classes


from typing import Any, Mapping, Optional
from twig_server.database.connection import Neo4jConnection
from neo4j import Neo4jDriver, Result, Record


class Node:
    def __init__(
        self, conn: Neo4jConnection, uid: Optional[int] = None
    ) -> None:
        """Initialize a new Node in Neo4J"""

        # represents properties locally
        self.properties: Mapping[str, Any] = {}

        # represents the data in the database
        self.db_obj: Optional[Record] = None

        self.properties["uid"] = uid
        self.conn: Neo4jConnection = conn
        self.db_conn: Neo4jDriver = conn.conn

        self.query_uid()  # try to retrieve existing database info for EXISTING UID

    # sync local properties with database data
    @classmethod
    def extract_properties(cls, db_obj: Any):
        assert db_obj is not None
        properties = {}
        properties["uid"] = int(db_obj.id)
        for key in db_obj._properties:
            properties[key] = db_obj[key]
        return properties
    def sync_properties(self) -> None:
        self.properties = {}
        if self.db_obj == None:
            return  # if no response, properties will be empty
        assert self.db_obj is not None  # for type checking
        self.properties = Node.extract_properties(self.db_obj)

    def query_uid(self, label_name: Optional[str] = None) -> Optional[Record]:
        if "uid" not in self.properties:  # querying for this UID
            return None
        queryStr = f"MATCH (n{(':'+label_name) if label_name else ''}) WHERE id(n)=$uid RETURN n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {"uid": self.properties["uid"]})
            self.db_obj = self.extract_node(res)
            self.sync_properties()
        return self.db_obj

    def delete(self) -> None:
        if "uid" not in self.properties:
            raise Exception("No UID to delete")
        queryStr = f"MATCH (n) WHERE id(n)=$uid DETACH DELETE n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {"uid": self.properties["uid"]})
            self.db_obj = self.extract_node(res)

            self.sync_properties()

    def create(self, label_name: str) -> Record:
        if "uid" in self.properties:
            if self.properties["uid"] is not None:
                return self.db_obj
        queryStr = (
            f"CREATE (n{(':'+label_name) if label_name else ''}) RETURN n"
        )
        with self.db_conn.session() as session:
            res: Result = session.run(queryStr)
            self.db_obj = self.extract_node(res)
            self.sync_properties()
        return self.db_obj

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
            self.db_obj = self.extract_node(res)
            self.sync_properties()
        return self.db_obj

    def get(self, name: str) -> Optional[str]:
        if name not in self.properties:
            return None
        return str(self.properties[name])


class Relationship:
    def __init__(self, conn: Neo4jConnection, **kwargs: Any):
        """Creates/Queries a Relationship in neo4j
        :param conn:
            Neo4J connection
        :Keyword Arguments:
            * uid -- Unique ID
            * a_id -- neo4j UID of source node
            * b_id -- neo4j UID of target node
        """
        self.properties = {}
        self.db_obj: Optional[Record] = None
        uid = kwargs.get("uid", None)
        if uid:
            self.properties["uid"] = int(uid)
        self.a_id: Optional[str] = kwargs.get("a_id", None)
        self.b_id: Optional[str] = kwargs.get("b_id", None)
        self.conn: Neo4jConnection = conn
        self.db_conn: Neo4jDriver = conn.conn
        # self.query_uid()

    def create(self, label_name: Optional[str] = None) -> Optional[Record]:
        if "uid" in self.properties:
            if self.properties["uid"] is not None:
                return self.db_obj
        if self.a_id is None or self.b_id is None:
            return None
        queryStr = f"MATCH (a),(b) \
              WHERE id(a)=$a_id AND id(b)=$b_id \
              CREATE (a)-[n{(':'+label_name) if label_name else ''}]->(b) RETURN n"
        with self.db_conn.session() as session:
            res: Result = session.run(
                queryStr, {"a_id": int(self.a_id), "b_id": int(self.b_id)}
            )
            self.db_obj = self.extract_relationship(res)
            self.sync_properties()
        return self.db_obj

    def extract_relationship(self, res: Result) -> Optional[Record]:
        row = res.single()
        if row:
            row = row[0]
        else:
            return None
        return row

    @classmethod # TODO abstract this away (redefinition in Node)
    def extract_properties(cls, db_obj: Any):
        assert db_obj is not None
        properties = {}
        properties["uid"] = int(db_obj.id)
        for key in db_obj._properties:
            properties[key] = db_obj[key]
        return properties
    # sync local properties with database data
    def sync_properties(self) -> None:
        self.properties = {}
        if self.db_obj == None:
            return  # if no response, properties will be empty
        assert self.db_obj is not None  # for type checking
        self.properties = Relationship.extract_properties(self.db_obj)

    def query_uid(self, label_name: Optional[str] = None) -> Optional[Result]:
        queryStr: str = f"MATCH (a)-[n{(':'+label_name) if label_name else ''}]->(b) WHERE id(n)=$uid RETURN n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {"uid": self.properties["uid"]})
            self.db_obj = self.extract_relationship(res)
            self.sync_properties()

        return self.db_obj
