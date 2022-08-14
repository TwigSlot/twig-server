from twig_server.database.connection import Neo4jConnection
from twig_server.database.Native import Node, Relationship


class Resource(Node):
    label_name = "Resource"

    def __init__(
        self, conn, 
        uid=None # passing in an EXISTING UID means we are QUERYING only, NO CREATION
    ):  # retrieve an existing resource or create a new one
        super().__init__()
        self.properties = {}
        self.properties['uid'] = uid
        self.db_conn = conn.conn
        self.query_uid()  # try to retrieve existing database info for EXISTING UID

    # sync local properties with database data
    def syncProperties(self):
        self.properties = {}
        if(self.dbObj == None): return # if no response, properties will be empty
        self.properties['uid'] = int(self.dbObj.id) 
        for key in self.dbObj._properties:
            self.properties[key] = self.dbObj[key]

    def query_uid(self):
        if 'uid' not in self.properties: # querying for this UID
            return None
        queryStr = f"MATCH (n:{Resource.label_name}) WHERE id(n)=$uid RETURN n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {"uid": self.properties['uid']})
            self.dbObj = self.extractNode(res)
            self.syncProperties()
        return self.dbObj

    def create(self):
        if 'uid' in self.properties: 
            return self.dbObj
        queryStr = f"CREATE (n:{Resource.label_name}) RETURN n"
        with self.db_conn.session() as session:
            res = session.run(queryStr)
            self.dbObj = self.extractNode(res)
            self.syncProperties()
        return self.dbObj
    
    def delete(self):
        if 'uid' not in self.properties:
            raise Exception("No UID to delete")
        queryStr = f"MATCH (n:{Resource.label_name}) WHERE id(n)=$uid DETACH DELETE n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {"uid": self.properties['uid']})
            self.dbObj = self.extractNode(res)

            self.syncProperties()
