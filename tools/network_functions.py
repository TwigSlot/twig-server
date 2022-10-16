"""
Helper functions that access the datastores for seeding the dev db with
dummy data.
"""
import requests

from tools.datamodels import User
from twig_server.database.User import User as TwigUser
from twig_server.database.connection import Neo4jConnection


def fetch_schemas(sess: requests.Session, kratos_endpoint: str):
    """
    Fetches the user identity schemas from Kratos

    Args:
        sess: The requests session to use
        kratos_endpoint: The kratos non-admin endpoint to use.

    Returns:
        The user schemas in json

    Raises:
        requests.exceptions.HTTPError: If the request fails.
    """
    resp = sess.get(f"{kratos_endpoint}/schemas")
    resp.raise_for_status()
    return resp.json()


def create_user(user: User, *, admin_endpoint: str, sess: requests.Session):
    """
    Inserts a user into kratos.

    Args:
        user: The User object to insert into kratos.
        admin_endpoint: The base url of the kratos admin endpoint
        sess: The session to use.

    Returns:
        The requests.Response object returned from the request.

    Notes:
        I do not raise_for_status here because it might be useful to continue to
        create users even if 1 creation fails. For example, a possible case would
        be if you added more users. The creation endpoint actually returns a non-success
        status code if you are inserting a user that already exists.
        Technically, I should be raising, so I will change this behavior in the future.
    """
    response = sess.post(
        f"{admin_endpoint}/admin/identities", json=user.to_kratos_schema()
    )
    return response


def get_all_users(sess: requests.Session, kratos_admin_endpoint: str):
    """
    Fetches all users from kratos in json format

    Args:
        sess: The requests session
        kratos_admin_endpoint: The kratos admin endpoint

    Returns:
        The json response from kratos. Likely a list of user schemas.
    """
    resp = sess.get(f"{kratos_admin_endpoint}/admin/identities")
    resp.raise_for_status()
    return resp.json()


def delete_user_from_kratos(
    user_id: str, sess: requests.Session, kratos_admin_endpoint: str
):
    """
    Deletes a user from kratos by their kratos user id.
    It doesn't really matter whether you run this before or after delete_user_from_neo4j

    Args:
        user_id: The kratos user id
        sess: The requests session
        kratos_admin_endpoint: The kratos admin endpoint

    Returns:
        Nothing

    Raises:
        requests.exceptions.HTTPError: If the request fails (aka, not 204)
    """
    resp = sess.delete(f"{kratos_admin_endpoint}/admin/identities/{user_id}")
    resp.raise_for_status()


def delete_user_from_neo4j(user_id: str, conn: Neo4jConnection):
    """
    Deletes a user from neo4j by their kratos user id

    Args:
        user_id: The user's kratos user id
        conn: The neo4j connection

    Returns:
        Nothing

    Raises:
        Might raise if it fails to delete, idk man
    """
    user = TwigUser(conn, username="doesnt_matter", kratos_user_id=user_id)
    user.delete_kratos_user_id()
