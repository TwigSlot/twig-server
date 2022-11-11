"""
Some models we use in TwigSlot

Notes:
    :class`Project` basically act like a folder which contains :class:`Resource`.

    :class:`Resource` is the basic unit of data in TwigSlot.
    Usually, it's a link to some online URL, with an optional description.

    :class:`Tag` is a label for :class:`Resource`. This kind of behaves
    like the macOS Finder's tag system. It allows you to categorize the
    resources.

Notes:
    Welcome beginners! iff means if and only if. Please do not mistake 'iff'
    as a typo.

    Please see: https://en.wikipedia.org/wiki/If_and_only_if for the full
    explanation of what iff means.

    Here's the short explanation.
    Consider the following statement P iff Q.
    If P is true, then you know certainly Q is true.
    If Q is true, then you know certainly P is true.

"""
import uuid
from typing import Optional

from pydantic import BaseModel, validator, Field
from pydantic.color import Color

from twig_server.models import ResourceGraph
from twig_server.models.db_objects import BaseTwigObject
from twig_server.models.types import ResourceId, TagId, ProjectId


class Tag(BaseTwigObject[TagId]):
    """
    Tags which can be applied to Resources.
    They sort of behave like Finder tags.
    """

    __label_name__ = "tag"
    # Tags have a color to make them nice and pretty!
    color: Color = Field(...)


class Resource(BaseTwigObject[ResourceId]):
    """
    A TwigSlot Resource, usually a link to a webpage.
    However, could contain anything really.

    Notes:
        We define a resource as being modified iff
         - The name of the resource was changed
         - The description of the resource was changed
         - The url of the resource was changed
    """

    __label_name__ = "resource"
    # URL of the resource
    url: Optional[str]

    @validator("url")
    def url_not_empty(cls, v):
        if v == "":
            raise ValueError("url should not be an empty string")
        return v

    def add_tag(self, tag: Tag):
        """
        Adds a tag to this resource.
        """
        # TODO: This nice interface
        raise NotImplementedError("Not done yet")


class Project(BaseTwigObject[ProjectId]):
    """
    Internal Representation of a TwigSlot Project

    Notes:
        We define a project as being modified iff:
         - the resource models was modified
         - the project description was modified
         - the project name was modified
         - the owner of the project was modified
         - ok wow, in hindsight, maybe we should track modifications somewhere else.
         TODO: so we should log every modification, yeah?
    """

    __label_name__ = "project"
    # The ID of the user who owns this project.
    owner: uuid.UUID

    resources: Optional[ResourceGraph]

    def add_resource(self, resource: Resource):
        """
        Adds a resource to this project. The resource need not exist in
        the database yet.

        Args:
            resource: The resource to add.

        Notes:
            The Cypher query string for creating a resource is:

            ```cypher
            MATCH (p:project)
            WHERE id(p) = $project_id
            CREATE (p)-[:has_resource]->(r:resource)
            SET r = $resource
            RETURN id(r)
            ```

            and the parameters that need to be filled in are
            `project_id` - obvious
            `resource` - just serialize the resource for neo4j insert.

        Returns:
            None
        """
        # TODO: This nice interface to add resources.
        # Try to handle for both when the project is newly created and has no ID
        # and when the project was pulled from a database.
        # Consider: project does not have an ID (newly created)
        # project does have an ID (from DB)

        # consider: resource does not have an ID (newly created)
        # resource does have an ID (from DB) - should we reject it?
        raise NotImplementedError("Still TODO")

    def add_resources(self, resources: list[Resource]):
        """
        Adds multiple resources to the project.

        Args:
            resources: The resources to add to the project.

        Returns:
            None
        """
        raise NotImplementedError("Not done yet")

    def add_resource_graph(self, graph: ResourceGraph):
        """
        Adds multiple resources in a graph to the project

        Args:
            graph: The resource graph to add.

        Returns:
            None
        """
        # TODO: Do we need this?
        raise NotImplementedError("Not done yet")

    def add_tag(self, tag: Tag):
        """
        Adds a tag to this project. If the tag does not exist in the database,
        it will be created upon commit.

        Args:
            tag: The tag to add to the project.

        Returns:
            None
        """
        # TODO: This nice interface to add tags.
        pass


class ProjectDisplaySettings(BaseModel):
    """
    Used to customize how your project models appears on the frontend

    Notes:
        This is decoupled from the actual data of the Project and Resource itself
        because it's not really part of the data model. It's more of a UI thing.
    """
