from twig_server.database.connection import Neo4jConnection
from twig_server.database.native import Node, Relationship


class Resource(Node):
    _label_name = "Resource"

    def __init__(
        self,
        conn,
        uid=None,  # passing in an EXISTING UID means we are QUERYING only, NO CREATION
    ):  # retrieve an existing resource or create a new one
        super().__init__(conn, uid)

    def query_uid(self):
        return super().query_uid(Resource._label_name)

    def create(self):
        return super().create(Resource._label_name)
