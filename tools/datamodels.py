"""
This file contains some useful data models which I created
for the ease of insertion of dummy data into the database.

Notes:
    This is not adapted for direct use in the main API.

Notes:
    Hello tch, if you are reading this, feel free to use this
    as a reference to how you design your own data models!
"""
import dataclasses
import warnings
from typing import Optional

from twig_server.database.User import User as TwigUser
from twig_server.database.Project import Project as TwigProject
from twig_server.database.Resource import Resource as TwigResource
from twig_server.database.connection import Neo4jConnection


@dataclasses.dataclass
class User:
    """
    A deserialization of the user object from `dev_dummy_data/users.yml`

    Notes:
        See `dev_dummy_data/users.yml` for more information on the format.
        You can just copy it blindly.

    Notes:
        So, I'm not validating if the user_id, username or password are
        empty. I'm also not checking if the username is a valid email.
        Please don't send empty data!!
    """

    username: str  # Note that this is also the email!
    password: Optional[
        str
    ]  # If password is None then this object was constructed by the kratos
    # response
    first_name: str
    last_name: str
    kratos_id: Optional[
        str
    ]  # Should be filled in only by the `create_user` function
    neo4j_node_id: Optional[
        int
    ]  # Should be filled in only by the `create_user` function

    @staticmethod
    def deserialize(user_dict: dict):
        """
        Deserializes a user from the dictionary representation

        Args:
            user_dict: The dictionary representation of the user

        Returns:
            The deserialized user

        Examples:
            >>> User.deserialize({"user_id": "123",
            ... "username": "test",
            ... "password": "test",
            ... "first_name": "test", "last_name": "test"})
        """
        return User(**user_dict, kratos_id=None, neo4j_node_id=None)

    @staticmethod
    def deserialize_all(user_dicts: list[dict]) -> list["User"]:
        """
        Deserializes a list of users from the dictionary representation

        Args:
            user_dicts: The dictionary representation of the users

        Returns:
            The deserialized users

        Examples:
            >>> from yaml import load, Loader
            >>> with open("dev_dummy_data/users.yml", "r") as f:
            ...     users = load(f, Loader=Loader)
            >>> all_the_users = User.deserialize_all(users)
        """
        return [User.deserialize(user_dict) for user_dict in user_dicts]

    def serialize(self) -> dict:
        """
        Serializes the user into a dictionary representation

        Returns:
            The serialized user

        Examples:
            >>> User.deserialize({"user_id": "123",
            ... "username": "test",
            ... "password": "test",
            ... "first_name": "test", "last_name": "test"}).serialize()
        """
        return dataclasses.asdict(self)

    def to_kratos_schema(self) -> dict:
        """
        Turns this user object into the format that kratos expects.
        You can directly use this in a POST to the kratos identity creation admin
        endpoint.

        Notes:
            This is VERY heavily hardcoded (as is intuitively obvious
            to the most casual observer) and should not be relied upon
            except in development

        Returns:
            The format that kratos wants
        """
        return {
            "credentials": {
                "password": {"config": {"password": self.password}}
            },
            "state": "active",
            "schema_id": "default",  # NOTE: Definitely hardcoded, lol
            "traits": {
                "email": self.username,
                "name": {"first": self.first_name, "last": self.last_name},
            },
            "verifiable_addresses": [
                {
                    # Note: the user_id doesn't actually seem to affect anything!
                    "status": "verified",
                    "value": self.username,
                    "verified": True,
                    "via": "default",  # see above, this is hardcoded.
                }
            ],
        }

    @staticmethod
    def from_kratos_schema(kratos_user: dict) -> "User":
        """
        Converts a user from the kratos schema into a user object

        Args:
            kratos_user: The kratos user schema

        Returns:
            The user object
        """
        return User(
            username=kratos_user["traits"]["email"],
            password=None,
            first_name=kratos_user["traits"]["name"]["first"],
            last_name=kratos_user["traits"]["name"]["last"],
            kratos_id=kratos_user["id"],
            neo4j_node_id=None,
        )

    @staticmethod
    def from_kratos_schemas(kratos_response: list[dict]) -> list["User"]:
        """
        Converts a list of kratos users into a list of user objects

        Args:
            kratos_response: The kratos user schema

        Returns:
            The user objects
        """
        return [User.from_kratos_schema(user) for user in kratos_response]

    def to_twig_user(self, neo4j_conn: Neo4jConnection) -> TwigUser:
        """
        Converts this user object into a TWIG user object

        Notes:
            At the time of writing, the twig user object has a couple of
            inefficiencies. So this method will automatically stuff the
            kratos id and any other relevant bits of information into the
            Twig user object to minimize inefficiencies.

        Notes:
            TWIG User should definitely not need to know about Neo4jConnection,
            but again at the time of writing it does. pls fix tch

        Args:
            neo4j_conn: The neo4j connection to use

        Returns:
            A twig user object

        Raises:
            ValueError: If the user does not have a kratos id. This is probably
            if you directly tried to create a twig user object from a user
            loaded from the file, instead of a mutated user object returned from the
            seed_users function.
        """
        if self.kratos_id is None:
            raise ValueError("User does not have a kratos id!")
        # So, reading the TwigUser class, I'm not really sure
        # whether specifying a kratos_user_id and a username is causing
        # an excess database call. Please refactor lol.
        twig_user = TwigUser(
            conn=neo4j_conn,
            kratos_user_id=self.kratos_id,
            username=self.username,
        )
        return twig_user


@dataclasses.dataclass
class Resource:
    """
    A resource that belongs to a project.

    See Also:
        ``twig_server.database.Resource.Resource``
    """

    neo4j_id: Optional[int]
    name: str
    description: str

    @staticmethod
    def deserialize(resource_dict: dict) -> "Resource":
        """
        Deserializes a resource from the dictionary representation

        Args:
            resource_dict: The dictionary representation of the resource

        Returns:
            The deserialized resource

        Examples:
            >>> Resource.deserialize({"name": "test",
            ... "description": "test"})
        """
        return Resource(**resource_dict, neo4j_id=None)

    def to_twig_resource(
        self, project: TwigProject, neo4j_conn: Neo4jConnection
    ) -> TwigResource:
        """
        Converts this resource object into a TWIG resource object

        Notes:
            At the time of writing, the twig resource object has a couple of
            inefficiencies. So this method will automatically stuff the
            neo4j id into the Twig resource object to minimize inefficiencies.

        Notes:
            TWIG Resource should definitely not need to know about Neo4jConnection,
            but again at the time of writing it does. pls fix tch

        Args:
            project: The project that this resource belongs to
            neo4j_conn: The neo4j connection to use

        Returns:
            A twig resource object

        Raises:
            ValueError: If the resource does not have a neo4j id. This is probably
            if you directly tried to create a twig resource object from a resource
            loaded from the file, instead of a mutated resource object returned from the
            seed_resources function.
        """
        twig_resource = TwigResource(conn=neo4j_conn,
                                     name=self.name,
                                     description=self.description,
                                     project=project)
        return twig_resource


@dataclasses.dataclass
class Project:
    """
    A deserialization of the project object from `dev_dummy_data/projects.yml`
    """

    neo4j_id: Optional[int]
    project_name: str
    owner_username: str
    project_description: str
    resources: list[Resource]

    @staticmethod
    def deserialize(owner_username: str, project_dict: dict) -> "Project":
        """
        Deserializes a project from a dictionary representation

        Args:
            owner_username: The username of the owner of the project
            project_dict: The dictionary representation of the project

        Returns:
            The deserialized project
        """
        return Project(
            project_name=project_dict["name"],
            owner_username=owner_username,
            project_description=project_dict["description"],
            resources=[
                Resource.deserialize(resource)
                for resource in project_dict["resources"]
            ],
            neo4j_id=None,
        )

    @staticmethod
    def deserialize_all(
        owner_username: str, project_dicts: list[dict]
    ) -> list["Project"]:
        """
        Deserializes a list of projects from a list of dictionary representations

        Args:
            owner_username: The username of the owner of the project
            project_dicts: The dictionary representations of the projects

        Returns:
            The deserialized projects
        """
        return [
            Project.deserialize(owner_username, project_dict)
            for project_dict in project_dicts
        ]

    def to_twig_project(
        self, user: TwigUser, neo4j_conn: Neo4jConnection
    ) -> TwigProject:
        """
        Converts this project object into a TWIG project object

        Notes:
            At the time of writing, the TwigProject object has a couple of
            inefficiencies. I'm avoiding excess neo4j database calls
            by manually stuffing in as much information as possible so that
            TwigProject does not have to call out to the database. Pls fix tch.

        Notes:
            TwigProject should definitely not need to know about Neo4jConnection,
            but again at the time of writing it does. pls fix tch

        Args:
            user: The user that owns the project
            neo4j_conn: The neo4j connection to use

        Returns:
            A twig project object

        Raises:
            ValueError: If the user does not have a kratos id.
             See ``User.to_twig_user``
        """
        # twig_user = user.to_twig_user(neo4j_conn)
        # if user.neo4j_node_id is None:
        #     warnings.warn(
        #         "User does not have a neo4j node id! "
        #         "Incurring HEAVY database call!"
        #     )
        #     twig_user.sync_properties()
        #     # raise ValueError("User does not have a neo4j node id!")

        return TwigProject(neo4j_conn, name=self.project_name, owner=user)
