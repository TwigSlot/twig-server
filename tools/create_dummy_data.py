from pprint import pprint

import requests
import yaml
from rich.table import Table

from tools.datamodels import User

from twig_server.database.User import User as TwigUser

# Note: I'm not bothering to import CLoader because the file isn't very big atm.
from yaml import Loader

import pathlib
import argparse

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
        f"{admin_endpoint}/admin/identities",
        json=user.to_kratos_schema()
    )
    return response


def get_all_users(sess: requests.Session, kratos_admin_endpoint: str):
    resp = sess.get(f"{kratos_admin_endpoint}/admin/identities")
    resp.raise_for_status()
    return resp.json()


def delete_users_from_kratos(user_ids: list[str], sess: requests.Session,
                             kratos_admin_endpoint: str):
    for user_id in user_ids:
        resp = sess.delete(f"{kratos_admin_endpoint}/admin/identities/{user_id}")
        if resp.status_code != 204:
            print(f"Failed to delete user {user_id}")
            print(resp.text)
        else:
            print(f"Deleted user {user_id}")


def delete_users_from_neo4j(user_ids: list[str], conn: Neo4jConnection):
    for user_id in user_ids:
        user = TwigUser(conn, username="doesnt_matter", kratos_user_id=user_id)
        print(f"NEO4J: Deleting user {user_id}")
        user.delete_kratos_user_id()


def main():
    with open(f"{THIS_FILE_DIR}/dev_dummy_data/users.yml") as f:
        users = yaml.load(f, Loader=Loader)
        user_deets = Table(title="User information")
        user_deets.add_column("Username", style="cyan")
        user_deets.add_column("Password", style="green")
        user_deets.add_column("Kratos ID", style="magenta")
        user_deets.add_column("Neo4j Node #")

        failed_creations = Table(title="Failed users")
        failed_creations.add_column("Username", style="red")
        failed_creations.add_column("Error message")

        for user in users:
            creation_resp = create_user(**user)
            if creation_resp.status_code != 201:
                # print(f"Failed to create user {user['username']}")
                # print(creation_resp.text)
                failed_creations.add_row(user["username"], creation_resp.text)
            else:
                user_kratos_id = creation_resp.json()["id"]
                # bad variable name but wtv
                tch_user = TwigUser(conn=neo4j_conn, username=user["username"],
                                kratos_user_id=user_kratos_id)
                created_tch_user = tch_user.create()
                # print(created_tch_user.id)

                # print(
                #     f"Created user: {user['username']} | {user['password']} | "
                #     f"{user_kratos_id}")
                user_deets.add_row(user["username"], user["password"],
                                   user_kratos_id,
                                   str(created_tch_user.id))  # type: ignore
    if user_deets.row_count > 0:
        console.print(user_deets)
    if failed_creations.row_count > 0:
        console.print(failed_creations)


# check for IDENT_SCHM
# print(fetch_schemas()[0]["id"])
# pprint(fetch_schemas())
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["create", "delete", "list"])
    parser.add_argument("--grab-ids-only", action="store_true")
    args = parser.parse_args()
    if args.action == "delete":
        user_ids = [user["id"] for user in get_all_users()]
        delete_users_from_kratos(user_ids)
        delete_users_from_neo4j(user_ids, neo4j_conn)
    elif args.action == "create":
        main()
    elif args.action == "list":
        if args.grab_ids_only:
            for u in get_all_users():
                print(f"{u['traits']['email']} | {u['id']}")
        else:
            pprint(get_all_users())
