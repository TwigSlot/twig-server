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
    user_id: str  # Note: seems to be some sort of uuid4.
    username: str  # Note that this is also the email!
    password: str  # Note: plaintext
    first_name: str
    last_name: str

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
        return User(**user_dict)

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
                    "id": self.user_id,
                    "status": "verified",
                    "value": self.username,
                    "verified": True,
                    "via": "default"  # see above, this is hardcoded.
                }
            ]
        }

    @staticmethod
    def to_twig_user(user: "User", neo4j_conn: Neo4jConnection,
                     kratos_id: str) -> TwigUser:
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
            kratos_id: The kratos id to use

        Returns:
            A twig user object
        """
        return TwigUser(conn=neo4j_conn, kratos_user_id=kratos_id,
                        username=user.username)
