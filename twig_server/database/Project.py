from twig_server.database.connection import Neo4jConnection
from twig_server.database.native import Node, Relationship
from twig_server.database.User import User
from typing import Optional
from neo4j import Record


class Project(Node):
    _label_name = "Project"
    _label_owner_relationship = "Project_Owner"

    def __init__(
        self,
        conn: Neo4jConnection,
        uid: Optional[str] = None,
        name: str = "Untitled Project",
        owner: Optional[User] = None,
    ) -> None:
        super().__init__(conn, uid)
        self.name = name
        self.owner: Optional[User] = owner
        self.owner_rls: Optional[Relationship] = None

    def set_owner(self, owner: User) -> Optional[Relationship]:
        assert owner is not None
        self.owner = owner
        owner_id = owner.properties["uid"]
        proj_id = self.properties["uid"]
        self.owner_rls = Relationship(
            self.conn, a_id=owner_id, b_id=proj_id
        ).create(Project._label_owner_relationship)
        return self.owner_rls

    def create(self, owner: User) -> Record:
        self.db_obj = super().create(Project._label_name)
        self.sync_properties()
        self.set_owner(owner)
        return self.db_obj
