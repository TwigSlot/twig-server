"""
Contains lower-level DB objects. These are not really types, since
we are subclassing this for things we insert into the database.
"""
import datetime
from typing import Optional, Generic

from pydantic import BaseModel, validator, Field

from twig_server.models.types import VK


class BaseDbObject(Generic[VK], BaseModel):
    """
    A base object to build upon. Inherit this if you are writing
    a model that needs to be inserted into our graph database. This contains some
    trivial and uninteresting functionalities, such as:

    - maintaining the ID of the object in the database
    - recording the time that the object was created in the database
    - recording when any property (excluding the id) of this object was changed in
     the database
    """
    # Unique identifier for this resource object
    # Note: This should not be manually filled in, as it will be assigned by the db.
    id: Optional[VK] = Field(None, allow_mutation=False)

    # Time that this thing was created in the database in UTC.
    creation_time_utc: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, allow_mutation=False
    )

    # Time that ANY property of this object was changed in the database, in UTC.
    last_modification_time_utc: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow
    )

    class Config:
        validate_assignment = True
        # we want the datetime as a unix timestamp, for easy and consistent parsing.
        json_encoders = {
            datetime: lambda dt: dt.timestamp()
        }


class BaseTwigObject(BaseDbObject[VK]):
    """
    A base Twig Object. This is probably what you want to inherit if you are
    modelling something.

    `name` is simply the name of this object. For example, a resource could have
    "Bijection between [0, 1] and (0, 1)". A project could be named
    "Quantum Field Theory".

    `description` is well, self-explanatory. For example, a resource could have
    ""This proves that [0, 1] and (0, 1) are equinumerous" as a description. A project
    could have "Collection of my QFT notes" as a description.

    Note that the description should NOT be an empty string if provided.

    Notes:
        Implementation note: Apparently, the generic type needs to be passed through.
        https://mypy.readthedocs.io/en/stable/generics.html#defining-sub-classes-of
        -generic-classes
    """
    name: str = Field(..., min_length=1)
    description: Optional[str]

    @validator("description")
    def description_not_empty(cls, v):
        if v == "":
            raise ValueError("description should not be an empty string")
        return v
