from twig_server.database.Native import Node, Relationship
from twig_server.neo4j import neo4j_driver

class User(Node):
    label_name = 'User'

    def __init__(self, username: str):
        self.uid = None # id() in the database
        self.username = username # unique username
        try:
            self.query_username()
        except:
            self.dbObj = None
    
    def query_username(self):  # query a User by username
        if (self.username == None):
            raise Exception("Username is None")
        queryStr = f"MATCH (n:{User.label_name}) WHERE n.username=$username RETURN n"
        res = neo4j_driver.session().run(queryStr, {"username": self.username})
        self.dbObj = self.extractNode(res)
        return self.dbObj

    def query_uid(self):  # query a User by uid
        if (self.uid == None):
            raise Exception("ID is None")
        queryStr = f"MATCH (n:{User.label_name}) WHERE id(n)=$uid RETURN n"
        res = neo4j_driver.session().run(queryStr, {"uid": self.uid})
        return res.single()[0]

    def create(self): # create a new User in the database
        if (self.dbObj != None):
            return self.dbObj # already created in database
        queryStr = f"CREATE (n:{User.label_name}) SET n.username=$username RETURN n"
        res = neo4j_driver.session().run(queryStr, {"username": self.username})
        self.dbObj = self.extractNode(res)
        # TODO set uid and properties
        return self.dbObj

    def delete_uid(self): # delete a user by ID
        queryStr = f"MATCH (n:{User.label_name}) WHERE id(n)=$uid DETACH DELETE n"
        neo4j_driver.session().run(queryStr, {"uid": self.uid})
        self.dbObj = None

    def delete_username(self): # delete a user by username
        queryStr = f"MATCH (n:{User.label_name}) WHERE n.username=$username DETACH DELETE n"
        neo4j_driver.session().run(queryStr, {"username": self.username})
        self.dbObj = None

    def save(self): # save python object information to database
        if (self.uid == None): self.create()