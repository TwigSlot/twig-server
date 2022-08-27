from typing import Any, List, Optional
from twig_server.database.Project import Project
from twig_server.database.connection import Neo4jConnection
from twig_server.database.native import Node, Relationship

from neo4j import Record, Neo4jDriver

class Resource(Node):
    _label_name = "Resource"
    _label_project_relationship = "Has_Resource"

    def __init__(
        self,
        conn: Neo4jConnection,
        **kwargs: Any
    ) -> None:  # retrieve an existing resource or create a new one
        """Creates/Queries a Project Resource
        :param conn:
            Neo4J connection
        :Keyword Arguments:
            * uid: `str` -- Neo4J Unique ID
            * name: `str` -- Name of Resource
            * project: `Project` -- Primary project this resource belongs to
              TODO next time implement multiproject resource sharing
        """
        uid = kwargs.get("uid", None)
        name = kwargs.get("name", "Untitled Resource")
        project = kwargs.get("project", None)
        super().__init__(conn, uid)
        self.name: str = name
        self.description: str = "default description"
        self.project: Optional[Project] = project
        self.project_rls: Optional[Relationship] = None

    def set_project(self, project: Project) -> Optional[Relationship]:
        assert project is not None
        self.project = project
        project_id = project.properties['uid']
        resource_id = self.properties['uid']
        self.project_rls = Relationship(self.conn, a_id = project_id, b_id = resource_id)
        self.project_rls_db_obj = self.project_rls.create(Resource._label_project_relationship)
        self.project_rls.sync_properties()
        return self.project_rls_db_obj

    def query_uid(self):
        return super().query_uid(Resource._label_name)

    def create(self, project: Project) -> Record:
        self.db_obj = super().create(Resource._label_name)
        self.set("name", self.name)
        self.set("description", self.description)
        self.sync_properties()
        self.set_project(project)
        return self.db_obj

    @classmethod
    def list_resources(cls, db_conn: Neo4jDriver, project: Project) -> List[Record]:
        queryStr = \
            f"MATCH (n:{Project._label_name})\
                    -[e:{Resource._label_project_relationship}]->\
                    (m:{Resource._label_name}) \
                WHERE id(n)=$uid \
                RETURN n,e,m"
        res_list = []
        with db_conn.session() as session:
            res = session.run(queryStr, {'uid': project.properties['uid']})
            res_list = [x for x in res]
        return res_list