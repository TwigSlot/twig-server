"""
TwigSlot Types. These aren't modelling database objects. We usually do not
insert these into the database, and these are just useful for strict typing
within our codebase itself.
"""
from typing import TypeVar, Generic, Union

from pydantic import BaseModel

from twig_server.models.neo4j_specific import Neo4jId


class ResourceId(Neo4jId):
    """
    A model for the ID of a resource

    Notes:
        Unfortunately, there is no way for us to validate that you did not pass
        in something that is not a resource ID. So, please, don't.

    """

    pass


class ProjectId(Neo4jId):
    """
    A model for the ID of a project.

    Notes:
        Unfortunately, there is no way for us to validate that you did not pass
        in something that is not a project ID. So, please, don't.
    """

    pass


class TagId(Neo4jId):
    """
    A Model for the ID of a tag.

    Notes:
        Unfortunately, there is no way for us to validate that you did not pass
        in something that is not a tag ID. So, please, don't.
    """

    pass


"""The vertex key."""
VK = TypeVar("VK", bound=Union[ResourceId, ProjectId, TagId])
"""The actual rich object which is mapped to by the vertex key"""
VO = TypeVar("VO", bound=object)


class EdgeRelation(Generic[VK], BaseModel):
    """
    Defines a relationship between 2 vertices where (src)->(dst).
    For example, (resource_1)->(resource_2)
    A more concrete example would be
    (real analysis)->(topology)<-(abstract algebra)

    Be aware that this is a **DIRECTED** edge.
    """
    src: VK
    dst: VK


class Graph(Generic[VK, VO], BaseModel):
    """
    A stricter graph data structure.
    """
    vertices: dict[VK, VO]
    edges: set[EdgeRelation[VK]]

    def get(self, key: VK) -> VO:
        return self.vertices[key]

    class Config:
        validate_assignment = True
