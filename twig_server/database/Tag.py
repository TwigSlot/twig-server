from twig_server.database.connection import Neo4jConnection, Neo4jDriver
from twig_server.database.native import Node, Relationship
from twig_server.database.Project import Project
from typing import Any, List, Optional
from neo4j import Record
import twig_server.app as app


class Tag(Node):
    _label_name = "Tag"
    _label_project_relationship = "Project_Tag"
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
            * project: `Project` -- Project which Tag belongs to
        """
        uid: Optional[int] = kwargs.get("uid", None)
        name = kwargs.get("name", "Empty Tag")
        project = kwargs.get("project", None)
        super().__init__(conn, uid)
        self.name: str = name
        self.description: str = "default tag description"
        self.project: Optional[Project] = project
        self.project_rls: Optional[Relationship] = None

    def get_project(self) -> Optional[Project]:
        queryStr = \
            f"MATCH (n:{Project._label_name})\
                -[e:{Tag._label_project_relationship}]->\
                    (m:{Tag._label_name})\
            WHERE id(m)=$uid\
            RETURN n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {'uid': self.properties['uid']})
            one_res = res.single()
            project = Node.extract_properties(one_res.get(one_res._Record__keys[0]))
        return project

    def set_project(self, project: Project) -> Optional[Relationship]:
        assert project is not None
        self.project = project
        project_id = project.properties["uid"]
        tag_id = self.properties["uid"]
        self.project_rls = Relationship(self.conn, a_id=project_id, b_id=tag_id)
        self.project_rls_db_obj = self.project_rls.create(
            Tag._label_project_relationship
        )
        self.project_rls.sync_properties()
        return self.project_rls_db_obj

    def create(self, project: Project) -> Record:
        self.db_obj = super().create(Tag._label_name)
        app.app.logger.info('setting name')
        app.app.logger.info(self.name)
        self.set("name", self.name)
        self.set("description", self.description)
        self.sync_properties()
        self.set_project(project)
        return self.db_obj
    
    @classmethod
    def list_project_tags(cls, db_conn: Neo4jDriver, project: Project) -> List[Record]:
        """
        list tags associated with project
        """
        queryStr = \
            f"MATCH (n:{Project._label_name})\
                    -[e:{Tag._label_project_relationship}]->\
                    (m:{Tag._label_name}) \
              WHERE id(n)=$uid \
              RETURN n,e,m"
        res_list = []
        with db_conn.session() as session:
            res = session.run(queryStr, { 'uid': project.properties['uid'] })
            res_list = [x for x in res]
        return res_list