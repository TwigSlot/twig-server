"""Objects that model graphs in TwigSlot."""
from twig_server.models.twigslot_objects import Project, Resource, Tag
from twig_server.models.types import (
    Graph,
    ResourceId,
    ProjectId,
    TagId,
)


class ResourceGraph(Graph[ResourceId, Resource]):
    """
    Models the graph-based relationships between resources.

    Notes:
        This is not meant to be constructed manually, but
        rather returned as a result.
    """

    class Config:
        allow_mutation = False


class ProjectGraph(Graph[ProjectId, Project]):
    """
    Models the graph-based relationships between projects.
    """

    class Config:
        allow_mutation = False


class TagGraph(Graph[TagId, Tag]):
    """
    Models the graph-based relationships between tags
    """

    class Config:
        allow_mutation = False