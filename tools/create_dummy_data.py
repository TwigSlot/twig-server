from os import environ as env
from pprint import pprint
import requests
import rich

from rich.table import Table
from rich.console import Console

import json
import pathlib
import argparse

from twig_server.database.connection import Neo4jConnection
from twig_server.database.User import User
from twig_server.database.Project import Project

THIS_FILE_DIR = pathlib.Path(__file__).parent.resolve()

# Note: Needs the admin endpoint
KRATOS_ADMIN_ENDPOINT = "http://localhost:4434"
KRATOS_ENDPOINT = "http://localhost:4433"

session = requests.Session()

neo4j_conn = Neo4jConnection(
    username=env.get("NEO4J_USERNAME", "neo4j"),
    password=env.get("NEO4J_PASSWORD", "password"),
    url=env.get("NEO4J_URL", "bolt://localhost:7687"),
)

console = Console()

try:
    neo4j_conn.connect()
    # Assume it connected, I hate the warning, lmao
    # neo4j_conn.verify_connectivity()
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")
    exit(1)

IDENT_SCHM = "default"


def fetch_schemas(sess: requests.Session = session):
    resp = sess.get(f"{KRATOS_ENDPOINT}/schemas")
    resp.raise_for_status()
    return resp.json()


def create_user(user_id, username: str, password: str, first_name: str = "",
                last_name: str = "", *, sess: requests.Session = session):
    """
    Create a user with the given username and password.

    Args:
        user_id: UUID4 string of the user
        username: The **email** of the user.
        password: The password of the user.
        first_name: The first name of the user. Blank by default
        last_name: The last name of the user. Blank by default
        sess: The session to use.
    """
    # TODO: This is hardcoded and should probably depend on the schema, but oh well.
    response = sess.post(
        f"{KRATOS_ADMIN_ENDPOINT}/admin/identities",
        json={
            "credentials": {
                "password": {
                    "config": {
                        "password": password
                    }
                }
            },
            "state": "active",
            "schema_id": IDENT_SCHM,
            "traits": {
                "email": username,
                "name": {
                    "first": first_name,
                    "last": last_name
                }
            },
            "verifiable_addresses": [
                {
                    # TODO: This doesn't actually change anything, lmao
                    "id": user_id,
                    "status": "verified",
                    "value": username,
                    "verified": True,
                    "via": IDENT_SCHM
                }
            ]
        },
    )
    return response


def get_all_users(sess: requests.Session = session):
    resp = sess.get(f"{KRATOS_ADMIN_ENDPOINT}/admin/identities")
    resp.raise_for_status()
    return resp.json()


def delete_users_from_kratos(user_ids: list[str], sess: requests.Session = session):
    for user_id in user_ids:
        resp = sess.delete(f"{KRATOS_ADMIN_ENDPOINT}/admin/identities/{user_id}")
        if resp.status_code != 204:
            print(f"Failed to delete user {user_id}")
            print(resp.text)
        else:
            print(f"Deleted user {user_id}")


def delete_users_from_neo4j(user_ids: list[str], conn: Neo4jConnection):
    for user_id in user_ids:
        user = User(conn, username="doesnt_matter", kratos_user_id=user_id)
        print(f"NEO4J: Deleting user {user_id}")
        user.delete_kratos_user_id()


def main():
    with open(f"{THIS_FILE_DIR}/dev_dummy_data/users.json") as f:
        users = json.load(f)
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
                tch_user = User(conn=neo4j_conn, username=user["username"],
                                kratos_user_id=user_kratos_id)
                created_tch_user = tch_user.create()
                # print(created_tch_user.id)

                # print(
                #     f"Created user: {user['username']} | {user['password']} | "
                #     f"{user_kratos_id}")
                user_deets.add_row(user["username"], user["password"],
                                   user_kratos_id, str(created_tch_user.id))  # type: ignore
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
