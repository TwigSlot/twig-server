# parent classes for 'native' neo4j objects: Nodes and Relationships
# mostly holds helper classes

class Node:
    def __init__(self):
        print("set properties")
        self.properties = {} # properties of the object locally, call setProperties to sync
        self.dbObj = None # represents the data in the database
        return
    def setProperties(self, dbObj): # syncs dbObj and properties
        pass # TODO set properties to dbObj with some indexing

    def extractNode(self, res): # for queries that are meant to return a single node
        row = res.single() 
        if(row): row = row[0]
        else: return None
        return row

class Relationship:
    def __init__(self):
        return
    def extractRelationship(self, res):
        row = res.single()
        if(row): row = row[0]
        else: return None
        return row