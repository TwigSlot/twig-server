# parent classes for 'native' neo4j objects: Nodes and Relationships
# mostly holds helper classes


class Node:
    def __init__(self, conn, uid=None):
        print("set properties")
        self.properties = {}  # represents properties locally
        self.dbObj = None  # represents the data in the database

        self.properties['uid'] = uid
        self.db_conn = conn.conn

        self.query_uid()  # try to retrieve existing database info for EXISTING UID
        return

    # sync local properties with database data
    def syncProperties(self):
        self.properties = {}
        if (self.dbObj == None):
            return  # if no response, properties will be empty
        self.properties['uid'] = int(self.dbObj.id)
        for key in self.dbObj._properties:
            self.properties[key] = self.dbObj[key]

    def query_uid(self, label_name=None):
        if 'uid' not in self.properties:  # querying for this UID
            return None
        queryStr = f"MATCH (n{(':'+label_name) if label_name else ''}) WHERE id(n)=$uid RETURN n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {"uid": self.properties['uid']})
            self.dbObj = self.extractNode(res)
            self.syncProperties()
        return self.dbObj

    def delete(self):
        if 'uid' not in self.properties:
            raise Exception("No UID to delete")
        queryStr = f"MATCH (n) WHERE id(n)=$uid DETACH DELETE n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {"uid": self.properties['uid']})
            self.dbObj = self.extractNode(res)

            self.syncProperties()

    def create(self, label_name):
        if 'uid' in self.properties:
            return self.dbObj
        queryStr = f"CREATE (n{(':'+label_name) if label_name else ''}) RETURN n"
        with self.db_conn.session() as session:
            res = session.run(queryStr)
            self.dbObj = self.extractNode(res)
            self.syncProperties()
        return self.dbObj

    def extractNode(
        self, res
    ):  # for queries that are meant to return a single node
        row = res.single()
        if row:
            row = row[0]
        else:
            return None
        return row

    def set(self, name, value):
        if 'uid' not in self.properties: 
            return None
        queryStr = f"MATCH (n) WHERE id(n)=$uid SET n.`{name}` = $value RETURN n"
        with self.db_conn.session() as session:
            res = session.run(
                queryStr, {"uid": self.properties['uid'], "name": name, "value": value})
            self.dbObj = self.extractNode(res)
            self.syncProperties()
        return self.dbObj

    def get(self, name):
        if name not in self.properties: return None
        return self.properties[name]


class Relationship:
    def __init__(self):
        return

    def extractRelationship(self, res):
        row = res.single()
        if row:
            row = row[0]
        else:
            return None
        return row
