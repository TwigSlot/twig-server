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
from typing import Optional

from twig_server.database.User import User as TwigUser
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
    password: Optional[str]  # If password is None then this object was constructed by the kratos response
    first_name: str
    last_name: str
    kratos_id: Optional[str]  # Should be filled in only by the `create_user` function

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
        return User(**user_dict, kratos_id=None)

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
                "password": {
                    "config": {
                        "password": self.password
                    }
                }
            },
            "state": "active",
            "schema_id": "default",  # NOTE: Definitely hardcoded, lol
            "traits": {
                "email": self.username,
                "name": {
                    "first": self.first_name,
                    "last": self.last_name
                }
            },
            "verifiable_addresses": [
                {
                    # Note: the user_id doesn't actually seem to affect anything!
                    "status": "verified",
                    "value": self.username,
                    "verified": True,
                    "via": "default"  # see above, this is hardcoded.
                }
            ]
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
            kratos_id=kratos_user["id"]
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
            TWIGUser should definitely not need to know about Neo4jConnection,
            but again at the time of writing it does. pls fix tch

        Args:
            user: The user object to convert
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
        return TwigUser(conn=neo4j_conn, kratos_user_id=self.kratos_id,
                        username=self.username)
