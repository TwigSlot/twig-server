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

from twig_server.models.db_objects import BaseTwigObject
from twig_server.models.types import ResourceId, TagId, ProjectId
from twig_server.neo4j_orm_lite.orm import TwigNeoModel


class Resource(BaseTwigObject[ResourceId], TwigNeoModel[TagId]):
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


class Tag(BaseTwigObject[TagId], TwigNeoModel[TagId]):
    """
    Tags which can be applied to Resources.
    They sort of behave like Finder tags.
    """
    __label_name__ = "tag"
    # Tags have a color to make them nice and pretty!
    color: Color = Field(...)


class Project(BaseTwigObject[ProjectId], TwigNeoModel[ProjectId]):
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

    # A list of resources this project contains.
    # Note: This is not meant to be filled in manually.
    # TODO: Investigate whether we should leave this as a computed property or remove it
    #  altogether.
    # resources: Optional[ResourceGraph]


class ProjectDisplaySettings(BaseModel):
    """
    Used to customize how your project models appears on the frontend

    Notes:
        This is decoupled from the actual data of the Project and Resource itself
        because it's not really part of the data model. It's more of a UI thing.
    """
