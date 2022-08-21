from typing import Optional
from twig_server.database.native import Node, Relationship
from twig_server.database.connection import Neo4jConnection

from neo4j import Record


class User(Node):
    _label_name: str = "User"

    def __init__(self, conn: Neo4jConnection, **kwargs) -> None:
        r"""Creates/Queries a User Node in neo4j
        :param conn:
            Neo4J connection
        :Keyword Arguments:
            * uid -- Unique ID
            * username -- username
            * kratos_user_id -- identity ID from ory kratos
        """
        uid: int = kwargs.get("uid", None)
        self.username: str = kwargs.get("username", None)
        self.kratos_user_id: str = kwargs.get("kratos_user_id", None)
        super().__init__(conn, uid)
        if self.username != None:
            self.query_username()
        elif self.kratos_user_id != None:
            self.query_kratos_user_id()

    def query_username(self) -> Optional[Record]:  # query a User by username
        if self.username == None:
            return None
        queryStr = (
            f"MATCH (n:{User._label_name}) WHERE n.username=$username RETURN n"
        )
        with self.db_conn.session() as session:
            res = session.run(queryStr, {"username": self.username})
            self.db_obj = self.extract_node(res)
            self.sync_properties()
        return self.db_obj

    def query_kratos_user_id(self):
        if self.kratos_user_id == None:
            return
        queryStr = f"MATCH (n:{User._label_name}) WHERE n.kratos_user_id=$kratos_user_id RETURN n"
        with self.db_conn.session() as session:
            res = session.run(
                queryStr, {"kratos_user_id": self.kratos_user_id}
            )
            self.db_obj = self.extract_node(res)
            self.sync_properties()
        return self.db_obj

    def create(self):  # create a new User in the database
        super().create(User._label_name)
        self.set("kratos_user_id", self.kratos_user_id)
        if self.username != None:
            self.set("username", self.username)

        return self.db_obj

    def delete_uid(self):  # delete a user by ID
        queryStr = (
            f"MATCH (n:{User._label_name}) WHERE id(n)=$uid DETACH DELETE n"
        )

        self.db_conn.conn.session().run(queryStr, {"uid": self.uid})
        self.db_obj = None

    def delete_username(self):  # delete a user by username
        queryStr = f"MATCH (n:{User._label_name}) WHERE n.username=$username DETACH DELETE n"
        self.db_conn.conn.session().run(queryStr, {"username": self.username})
        self.db_obj = None

    def delete_kratos_user_id(self):
        queryStr = f"MATCH (n:{User._label_name}) WHERE n.kratos_user_id=$kratos_user_id DETACH DELETE n"
        self.db_conn.conn.session().run(queryStr, {"username": self.username})
        self.db_obj = None

    def save(self):  # save python object information to database
        if self.uid == None:
            self.create()
