from typing import ClassVar, Optional, Any

import neo4j

from twig_server.models.db_objects import BaseDbObject
from twig_server.neo4j_orm_lite.query import CypherQueryString, Operation, \
    PreparedCypherQuery


class TwigNeoModel:
    # TODO: Label name should be optional.
    __label_name__: ClassVar[str]

    @classmethod
    def get_all_query_str(cls) -> CypherQueryString:
        return CypherQueryString(
            Operation.MATCH,
            label_name=cls.__label_name__,
            returned_idx_name="n",
            returned_idx_type=list[cls],
            is_single=False,
            query_string=f"MATCH (n:{cls.__label_name__}) RETURN n",
        )

    @classmethod
    def _get_query_str(cls) -> CypherQueryString:
        query_string = (
            f"MATCH (n:{cls.__label_name__}) WHERE id(n)=$obj_id RETURN n"
        )
        return CypherQueryString(
            Operation.MATCH,
            label_name=cls.__label_name__,
            returned_idx_name="n",
            returned_idx_type=cls,
            required_parameters=[("obj_id", int)],
            is_single=True,
            query_string=query_string,
        )

    @classmethod
    def _create_query_str(cls):
        """Requires you to fill in props"""
        query_string = (
            f"CREATE (n:{cls.__label_name__}) SET n = $props RETURN id(n)"
        )
        return CypherQueryString(
            Operation.CREATE,
            label_name=cls.__label_name__,
            returned_idx_name="id(n)",
            returned_idx_type=int,
            is_single=True,
            required_parameters=[("props", dict)],
            query_string=query_string,
        )

    @classmethod
    def _update_query_str(cls):
        """Requires you to fill in new_data"""
        # TODO: Do a proper cypher update.
        #  See: https://neo4j.com/developer/cypher/updating/#cypher-update
        query_string = f"""
        MATCH (n:{cls.__label_name__})
        WHERE id(n)=$id
        SET n = $new_data
        RETURN id(n) 
        """
        return CypherQueryString(
            Operation.UPDATE_OVERWRITE,
            label_name=cls.__label_name__,
            returned_idx_name="id(n)",
            returned_idx_type=int,
            is_single=True,
            required_parameters=[("id", int), ("new_data", dict)],
            query_string=query_string,
        )

    @classmethod
    def _delete_query_str(cls):
        """Requires you to fill in id"""
        query_string = f"""
        MATCH (n:{cls.__label_name__})
        WHERE id(n)=$id
        DETACH DELETE n
        """
        return CypherQueryString(
            Operation.DELETE,
            label_name=cls.__label_name__,
            required_parameters=[("id", int)],
            query_string=query_string,
        )


class TwigORMSession:
    """
    Examples:
        >>> import uuid
        >>> import neo4j
        >>> from twig_server.models import Project, Resource, Tag
        >>> driver = neo4j.GraphDatabase.driver("bolt://localhost:7687",
        auth=("neo4j", "notneo4j"))
        >>> with TwigORMSession(driver) as sess:
        >>>    proj = Project(name="Test Project",
        >>>                      description="Test Description",
        >>>                      owner=uuid.uuid4())
        >>>    rsrc1 = Resource(name="Test Resource 1",
        >>>                     description="Test Description 1",
        >>>                     url="https://www.google.com")
        >>>    rsrc2 = Resource(name="Test Resource 2",
        >>>                     description="Test Description 2",
        >>>                     url="https://www.google.com")
        >>>    rsrc1.add_
        >>>    sess.add(proj)
        >>>    sess.commit()
    """

    def __init__(self, driver: neo4j.Neo4jDriver):
        self.driver = driver
        self.execution_log: list[tuple[Operation, BaseDbObject]] = []

    def __enter__(self):
        self.session = self.driver.session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def execute(self, query: PreparedCypherQuery):
        pass

    # TODO: Decouple from our BaseDbObject
    def add(self, obj: BaseDbObject):
        if not isinstance(obj, BaseDbObject):
            raise TypeError("Object must be a TwigNeoModel")
        if obj.id is None:
            self.execution_log.append((Operation.CREATE, obj))
        else:
            self.execution_log.append((Operation.UPDATE_OVERWRITE, obj))

    def add_all(self, objs: list[BaseDbObject]):
        for obj in objs:
            self.add(obj)

    def show_query(self) -> str:
        """
        Shows the query string that will be executed

        Returns:
            str: The query string that will be executed
        """
        return ';\n'.join([str(q) for op, q in self.execution_log])

    def get(self, obj_id: int) -> BaseDbObject:
        """Returns the object with the given id"""
        pq = PreparedCypherQuery(TwigNeoModel._get_query_str(), {
            "obj_id": obj_id
        })
        if self.session is None:
            raise RuntimeError("Session is not open")
        return BaseDbObject._convert_record(pq.execute(self.session))

    def commit(self) -> Optional[list[Any]]:
        """Commits the current session and returns the results"""
        if self.session is None:
            raise RuntimeError("Session is not open")
        with self.session as sess:
            results = []
            for op, obj in self.execution_log:
                if op == Operation.CREATE:
                    pq = obj.create()
                elif op == Operation.UPDATE_OVERWRITE:
                    pq = obj.update()
                elif op == Operation.DELETE:
                    pq = obj.delete()
                ret_val = pq.execute(sess)
                results.append(ret_val)
            return results if len(results) > 0 else None
