from twig_server.database.connection import Neo4jConnection
from twig_server.database.Native import Node, Relationship


class Resource(Node):
    label_name = "Resource"

    def __init__(
        self, uid=None
    ):  # retrieve an existing resource or create a new one
        super().__init__()
        self.properties = {"uid": uid}
        self.uid = None
        self.query_uid()  # try to retrieve existing database info
        self.db_conn = Neo4jConnection()
        self.db_conn.connect()
        if self.dbObj == None:
            self.create()

    def query_uid(self):
        if self.uid == None:
            return None
        queryStr = f"MATCH (n:{Resource.label_name}) WHERE id(n)=$uid RETURN n"
        res = self.db_conn.conn.session().run(queryStr, {"uid": self.uid})
        self.dbObj = self.extractNode(res)
        return self.dbObj

    def create(self):
        if self.uid != None:  # should be already created
            return self.dbObj
        queryStr = f"CREATE (n:{Resource.label_name}) RETURN n"
        res = self.db_conn.conn.session().run(queryStr, {"uid": self.uid})
        self.dbObj = self.extractNode(res)
        return self.dbObj
