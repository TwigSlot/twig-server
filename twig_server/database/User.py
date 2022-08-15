from twig_server.database.Native import Node, Relationship
from twig_server.database.connection import Neo4jConnection


class User(Node):
    label_name = "User"

    def __init__(self, conn, **kwargs):
        uid = kwargs.get("uid", None)
        self.username = kwargs.get("username", None)
        super().__init__(conn, uid)
        if self.username != None:
            self.query_username()

    def query_username(self):  # query a User by username
        if self.username == None:
            return
        queryStr = (
            f"MATCH (n:{User.label_name}) WHERE n.username=$username RETURN n"
        )
        with self.db_conn.session() as session:
            res = session.run(queryStr, {"username": self.username})
            self.dbObj = self.extractNode(res)
            self.syncProperties()
        return self.dbObj

    def create(self):  # create a new User in the database
        super().create(User.label_name)
        self.set("username", self.username)

        return self.dbObj

    def delete_uid(self):  # delete a user by ID
        queryStr = (
            f"MATCH (n:{User.label_name}) WHERE id(n)=$uid DETACH DELETE n"
        )
        self.db_conn.conn.session().run(queryStr, {"uid": self.uid})
        self.dbObj = None

    def delete_username(self):  # delete a user by username
        queryStr = f"MATCH (n:{User.label_name}) WHERE n.username=$username DETACH DELETE n"
        self.db_conn.conn.session().run(queryStr, {"username": self.username})
        self.dbObj = None

    def save(self):  # save python object information to database
        if self.uid == None:
            self.create()
