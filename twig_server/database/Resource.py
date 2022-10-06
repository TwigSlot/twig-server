from typing import Any, List, Optional
from twig_server.database.Project import Project
from twig_server.database.Tag import Tag
from twig_server.database.connection import Neo4jConnection
from twig_server.database.native import Node, Relationship

from neo4j import Record, Neo4jDriver

import twig_server.app as app

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

    def add_tag(self, tag: Tag) -> Optional[Relationship]:
        assert tag is not None
        resource_id = self.properties['uid']
        tag_id = tag.properties['uid']
        tag_rls = Relationship(self.conn, a_id = resource_id, b_id = tag_id)
        tag_rls_db_obj = tag_rls.create(Tag._label_resource_relationship)
        tag_rls.sync_properties()
        return tag_rls_db_obj

    def unjoin_tag(self, tag: Tag):
        pass

    def query_uid(self):
        return super().query_uid(Resource._label_name)

    def create(self, project: Project) -> Record:
        self.db_obj = super().create(Resource._label_name)
        self.set("name", self.name)
        self.set("description", self.description)
        self.sync_properties()
        self.set_project(project)
        return self.db_obj

    def find_rls_with(self, tag: Tag):
        queryStr = f"MATCH (n:{Resource._label_name})-[e]->(t:{Tag._label_name})"+\
                   f"WHERE id(n)=$uid AND id(t)=$tag_id RETURN e"
        rls_db_obj = None
        with self.db_conn.session() as session:
            res = session.run(
                queryStr,
                {
                    'uid': self.properties['uid'],
                    'tag_id': tag.properties['uid']
                }
            )
            rls_db_obj = Relationship.extract_relationship(res)
        return Relationship.extract_properties(rls_db_obj)


    @classmethod
    def update_all_positions(cls, db_conn: Neo4jConnection, new_positions: dict, project_id: int) -> None:
        for uid in new_positions:
            r = Resource(db_conn, uid=int(uid))
            r.query_uid()
            if(r.get_project().properties['uid'] != project_id):
                continue
            if('uid' in r.properties):
                r.update_position(new_positions[uid])

    def update_position(self, new_pos: dict) -> Record:
        if "uid" not in self.properties:
            return None
        queryStr = f"MATCH (n:{Resource._label_name}) WHERE id(n)=$uid SET n.pos_x = $x SET n.pos_y = $y RETURN n"
        with self.db_conn.session() as session:
            res = session.run(
                queryStr,
                {
                    'x': round(new_pos['x']),
                    'y': round(new_pos['y']),
                    'uid': self.properties['uid']
                }
            )
            self.db_obj = self.extract_node(res)
            self.sync_properties()
        return self.db_obj

    @classmethod
    def get_tagged_resources(cls, db_conn: Neo4jDriver, tag: Tag):
        queryStr = \
            f"MATCH (n:{Resource._label_name})\
                -[e:{Tag._label_resource_relationship}]->\
                    (m:{Tag._label_name})\
            WHERE id(m)=$uid\
            RETURN n"
        res_list = []
        with db_conn.session() as session:
            res = session.run(queryStr, { 'uid': tag.properties['uid'] })
            res_list = [x for x in res]
        return res_list


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
    @classmethod
    def list_resource_tags(cls, db_conn: Neo4jDriver, resource: Any) -> List[Record]:
        """
        list tags associated with project
        """
        queryStr = \
            f"MATCH (n:{Resource._label_name})\
                    -[e:{Tag._label_resource_relationship}]->\
                    (m:{Tag._label_name}) \
              WHERE id(n)=$uid \
              RETURN n,e,m"
        res_list = []
        with db_conn.session() as session:
            res = session.run(queryStr, { 'uid': resource.properties['uid'] })
            res_list = [x for x in res]
        return res_list
    def get_project(self) -> Project:
        queryStr = \
            f"MATCH (n:{Project._label_name})\
                    -[e:{Resource._label_project_relationship}]->\
                    (m:{Resource._label_name}) \
                WHERE id(m)=$uid \
                RETURN n"
        with self.db_conn.session() as session:
            res = session.run(queryStr, {'uid': self.properties['uid']})
            one_res = res.single()
            project_properties = Node.extract_properties(one_res.get(one_res._Record__keys[0]))
            self.project = Project(self.conn, uid=project_properties['uid'])
            self.project.sync_properties()
        return self.project