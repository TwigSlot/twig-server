from typing import ClassVar, Generic

import neo4j

from twig_server.models.db_objects import BaseDbObject
from twig_server.models.types import VK
from twig_server.neo4j_orm_lite.query import CypherQueryString, Operation


class TwigNeoModel(Generic[VK]):
    __label_name__: ClassVar[str]

    # TODO: Figure out how to just execute it and not return query strings.
    @classmethod
    def get_all(cls) -> CypherQueryString:
        return CypherQueryString(
            Operation.READ,
            returned_idx_name="n",
            is_single=False,
            query_string=f"MATCH (n:{cls.__label_name__}) RETURN n",
        )

    @classmethod
    def get(cls, obj_id: VK) -> CypherQueryString:
        query_string = (
            f"MATCH (n:{cls.__label_name__}) WHERE id(n)={obj_id} RETURN n"
        )
        return CypherQueryString(
            Operation.READ,
            returned_idx_name="n",
            is_single=True,
            query_string=query_string,
        )

    # TODO: Figure out how to make this a self, in particular, the
    #  parameters should be automatically filled in for you in this case.
    @classmethod
    def create(cls):
        """Requires you to fill in props"""
        query_string = (
            f"CREATE (n:{cls.__label_name__}) SET n = $props RETURN id(n)"
        )
        return CypherQueryString(
            Operation.CREATE,
            returned_idx_name="id(n)",
            is_single=True,
            required_parameters=["props"],
            query_string=query_string,
        )

    # TODO: Figure out how to make this a self, in particular, the
    #  parameters should be automatically filled in for you in this case.
    @classmethod
    def update(cls):
        """Requires you to fill in new_data"""
        # TODO: Do a proper cypher update.
        # https://neo4j.com/developer/cypher/updating/#cypher-update
        query_string = f"""
        MATCH (n:{cls.__label_name__})
        WHERE id(n)=$id
        SET n = $props
        RETURN id(n) 
        """
        return CypherQueryString(
            Operation.UPDATE,
            returned_idx_name="id(n)",
            is_single=True,
            required_parameters=["new_data"],
            query_string=query_string,
        )

    # TODO: Figure out how to make this a self, in particular, the
    #  parameters should be automatically filled in for you in this case.
    @classmethod
    def delete(cls):
        """Requires you to fill in id"""
        query_string = f"""
        MATCH (n:{cls.__label_name__})
        WHERE id(n)=$id
        DETACH DELETE n
        """
        return CypherQueryString(
            Operation.DELETE,
            required_parameters=["id"],
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

    def __enter__(self):
        self.session = self.driver.session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def execute(self, query: CypherQueryString):
        pass

    def add(self, obj: BaseDbObject):
        pass

    def add_all(self, objs: list[BaseDbObject]):
        pass

    def show_query(self) -> str:
        """
        Shows the query string that will be executed

        Returns:
            str: The query string that will be executed
        """
        pass
