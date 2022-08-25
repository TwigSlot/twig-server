from twig_server.database.connection import Neo4jConnection, Neo4jDriver
from twig_server.database.native import Node, Relationship
from twig_server.database.User import User
from typing import Any, List, Optional
from neo4j import Record


class Project(Node):
    _label_name = "Project"
    _label_owner_relationship = "Project_Owner"

    def __init__(
        self,
        conn: Neo4jConnection,
        **kwargs: Any,
    ) -> None:
        """Creates/Queries a Project Node
        :param conn:
            Neo4J connection
        :Keyword Arguments:
            * uid: `str` -- Neo4J Unique ID
            * name: `str` -- Name of Project
            * owner: `User` -- Owner of Project
        """
        uid: Optional[int] = kwargs.get("uid", None)
        name = kwargs.get("name", "Untitled Project")
        owner = kwargs.get("owner", None)
        super().__init__(conn, uid)
        self.name: str = name
        self.description: str = "This is the default project description"
        self.owner: Optional[User] = owner
        self.owner_rls: Optional[Relationship] = None

    def set_owner(self, owner: User) -> Optional[Relationship]:
        assert owner is not None
        self.owner = owner
        owner_id = owner.properties["uid"]
        proj_id = self.properties["uid"]
        self.owner_rls = Relationship(self.conn, a_id=owner_id, b_id=proj_id)
        self.owner_rls_db_obj = self.owner_rls.create(
            Project._label_owner_relationship
        )
        self.owner_rls.sync_properties()
        return self.owner_rls_db_obj

    def create(self, owner: User) -> Record:
        self.db_obj = super().create(Project._label_name)
        self.set("name", self.name)
        self.set("description", self.description)
        self.sync_properties()
        self.set_owner(owner)
        return self.db_obj

    @classmethod
    def list_projects(cls, db_conn: Neo4jDriver, user: User) -> List[Record]:
        queryStr = \
            f"MATCH (n:{User._label_name})\
                    -[e:{Project._label_owner_relationship}]->\
                    (m:{Project._label_name}) \
              WHERE id(n)=$uid \
              RETURN n,e,m"
        res_list = []
        with db_conn.session() as session:
            res = session.run(queryStr, { 'uid': user.properties['uid'] })
            res_list = [x for x in res]
        return res_list
