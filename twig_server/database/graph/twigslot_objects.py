"""
Some models we use in TwigSlot

Notes:
    :class`Project` basically act like a folder which contains :class:`Resource`.

    :class:`Resource` is the basic unit of data in TwigSlot.
    Usually, it's a link to some online URL, with an optional description.

    :class:`Tag` is a label for :class:`Resource`. This kind of behaves
    like the macOS Finder's tag system. It allows you to categorize the
    resources.
"""
import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, validator, Field


# TODO: This entire file needs to go somewhere else,
#  it's not graph db specific at all actually


class Resource(BaseModel):
    """
    A TwigSlot Resource, usually a link to a webpage.
    However, could contain anything really.
    """
    # Unique identifier for this resource object
    # Note: This is the Neo4j UID
    id: int

    # Name for the resource. For example:
    # "Bijection between [0, 1] and (0, 1)"
    name: str = Field(..., min_length=1)

    # Description for the resource. For example,
    # "This proves that [0, 1] and (0, 1) are equinumerous"
    # Note: Description should not be an empty string if provided
    description: Optional[str]

    # URL of the resource
    url: Optional[str]

    @validator('description')
    def description_not_empty(cls, v):
        if v == '':
            raise ValueError('description should not be an empty string')
        return v

    @validator('url')
    def url_not_empty(cls, v):
        if v == '':
            raise ValueError('url should not be an empty string')
        return v


class Tag(BaseModel):
    """
    Tags which can be applied to Resources.
    """


class Project(BaseModel):
    """
    Internal Representation of a TwigSlot Project
    """
    # Unique identifier for this project object
    # Note: This is the Neo4j UID. This will only be populated if pulled from
    # Neo4j. If creating a project, this might not exist.
    id: Optional[int]
    name: str  # Name of the project, kind of like a title
    # The ID of the user who owns this project.
    owner: uuid.UUID
    description: str  # Project description. This will probably be a markdown string.
    creation_time: datetime.datetime  # When the project was created

    # A list of resources this project contains.
    # This will only be populated if pulled from Neo4j.
    resources: Optional[list[Resource]]


class ProjectDisplaySettings(BaseModel):
    """
    Used to customize how your project graph appears on the frontend

    Notes:
        This is decoupled from the actual data of the Project and Resource itself
        because it's not really part of the data model. It's more of a UI thing.
    """
