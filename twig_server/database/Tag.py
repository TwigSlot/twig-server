from twig_server.database.connection import Neo4jConnection, Neo4jDriver
from twig_server.database.native import Node, Relationship
from twig_server.database.User import User
from typing import Any, List, Optional
from neo4j import Record


class Tag(Node):
    _label_name = "Tag"
    _label_owner_relationship = "Tag_Owner"
    _label_resource_relationship = "Resource_Tag"

    def __init__(
        self,
        conn: Neo4jConnection,
        **kwargs: Any,
    ) -> None:
        """Creates/Queries a Tag Node
        :param conn:
            Neo4J connection
        :Keyword Arguments:
            * uid: `str` -- Neo4J Unique ID
            * name: `str` -- Name of Tag
            * owner: `User` -- Owner of Tag
        """
        uid: Optional[int] = kwargs.get("uid", None)
        name = kwargs.get("name", "Empty Tag")
        owner = kwargs.get("owner", None)
        super().__init__(conn, uid)
        self.name: str = name
        self.description: str = "default tag description"
        self.owner: Optional[User] = owner
        self.owner_rls: Optional[Relationship] = None

    def get_owner(self) -> Optional[User]:
        queryStr = \
            f"MATCH (n:{User._label_name})\
                -[e:{Tag._label_owner_relationship}]->\
                    (m:{Tag._label_name})\
            WHERE id(m)=$uid\
            RETURN n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {'uid': self.properties['uid']})
            one_res = res.single()
            user = Node.extract_properties(one_res.get(one_res._Record__keys[0]))
        return user

    def set_owner(self, owner: User) -> Optional[Relationship]:
        assert owner is not None
        self.owner = owner
        owner_id = owner.properties["uid"]
        proj_id = self.properties["uid"]
        self.owner_rls = Relationship(self.conn, a_id=owner_id, b_id=proj_id)
        self.owner_rls_db_obj = self.owner_rls.create(
            Tag._label_owner_relationship
        )
        self.owner_rls.sync_properties()
        return self.owner_rls_db_obj

    def create(self, owner: User) -> Record:
        self.db_obj = super().create(Tag._label_name)
        self.set("name", self.name)
        self.set("description", self.description)
        self.sync_properties()
        self.set_owner(owner)
        return self.db_obj

    @classmethod
    def list_tags(cls, db_conn: Neo4jDriver, user: User) -> List[Record]:
        """
        list tags associated with user
        """
        queryStr = \
            f"MATCH (n:{User._label_name})\
                    -[e:{Tag._label_owner_relationship}]->\
                    (m:{Tag._label_name}) \
              WHERE id(n)=$uid \
              RETURN n,e,m"
        res_list = []
        with db_conn.session() as session:
            res = session.run(queryStr, { 'uid': user.properties['uid'] })
            res_list = [x for x in res]
        return res_list