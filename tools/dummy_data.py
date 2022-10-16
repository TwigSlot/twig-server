import logging
from os import environ as env
import argparse
import pathlib
from typing import Optional

import requests
import yaml
from rich.table import Table
from rich.console import Console

from dotenv import load_dotenv
from yaml import Loader

from tools.create_dummy_data import fetch_schemas, get_all_users, create_user
from tools.datamodels import User
from twig_server.database.connection import Neo4jConnection


def check_environment_vars_setup():
    """
    Checks that the environment variables are set up correctly

    Returns:
        Nothing

    Raises:
        Will immediately raise ValueError as soon as a single
        environment variable is not set up correctly
    """
    vars_to_check = [
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "NEO4J_SERVER_URL",
        "KRATOS_ADMIN_ENDPOINT",
        "KRATOS_ENDPOINT",
    ]
    for env_var in vars_to_check:
        if env_var not in env:
            raise ValueError(f"Environment variable `{env_var}` not set!")


def seed_users(neo4j_conn: Neo4jConnection,
               sess: requests.Session,
               users: list[dict],
               *, logger: Optional[logging.Logger] = None) -> tuple[list[User],
                                                                    list[User]]:
    """
    Seeds all the users into the database.

    Notes:
        Currently due to non-optimal factoring this also actually requires us
        to insert the users into the Neo4j database. Future work by tch (or me) will
        eliminate this dependency.

    Args:
        users: List of users in the proper format
        neo4j_conn: The neo4j connection
        sess: The requests session
        logger: Optionally, a logger for us to send logging information into.

    Returns:
        Tuple of (successfully_created_users, unsuccessfully_created_users)

    Raises:
        Will raise if we cannot connect to any of the data stores.
        Will also raise if we encounter a non-success HTTP response code
        when attempting to perform any operation.
    """
    users_list = User.deserialize_all(users)
    for user in users_list:
        creation_resp = create_user(user, admin_endpoint=env["KRATOS_ADMIN_ENDPOINT"])


def create_connections_and_test(logger: Optional[logging.Logger] = None) -> tuple[
    Neo4jConnection, requests.Session]:
    """
    Creates the necessary connections to Neo4j and kratos,
    and tests them out.

    Returns:
        Tuple of Neo4jConnection and requests.Session

    Notes:
        There is nothing special about this requests.Session specifically.
    """

    neo4j_connection = Neo4jConnection(
        username=env["NEO4J_USERNAME"],
        password=env["NEO4J_PASSWORD"],
        url=env["NEO4J_SERVER_URL"],
    )

    sess = requests.Session()

    # test if neo4j is active
    try:
        neo4j_connection.connect()
    except Exception as e:
        logger.error("Looks like we could not connect to Neo4j. "
                     "Please check if it is running!")
        raise e

    # test kratos endpoints
    try:
        sess.get(env["KRATOS_ENDPOINT"]).raise_for_status()
        sess.get(env["KRATOS_ADMIN_ENDPOINT"]).raise_for_status()
    except requests.HTTPError as e:
        logger.error("Looks like we could not connect to Kratos. "
                     "Please check if it is running!")
        raise e
    return neo4j_connection, sess


def seed_datastores(
        dummy_data_folder: pathlib.Path,
        neo4j_conn: Neo4jConnection,
        sess: requests.Session,
        logger: Optional[logging.Logger] = None):
    """
    Fully seed all datastores.

    This will seed Kratos with some development users, and Neo4j with
    some projects associated with those development users

    Args:
        dummy_data_folder: The folder which contains the dummy data.
                        Should be named `dev_dummy_data`
        neo4j_conn: The Neo4j connection to use
        sess: The requests session to use
        logger: Optionally, a logger for us to send logging information into.

    Returns:
        Tuple of (successfully_created_users, unsuccessfully_created_users)

    Raises:
        Will raise if we cannot connect to any of the datastores.
    """
    with open(dummy_data_folder / "users.yml", 'r') as users_file:
        users = yaml.load(users_file, Loader=Loader)


if __name__ == "__main__":
    THIS_FILE_DIR = pathlib.Path(__file__).parent.resolve()
    terminal = Console()

    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(title="Action",
                                                 required=True,
                                                 description="The main action to "
                                                             "perform.")
    action.add_argument("-i", "--info", action="store_true",
                        help="Pretty-print the Kratos identity schema")
    action.add_argument("-c", "--create", action="store_true",
                        help="Seeds all data stores with dummy data, creating all the "
                             "users projects and resources")
    action.add_argument("-d", "--delete", action="store_true",
                        help="Purges all data from the data stores")
    action.add_argument("-l", "--list", action="store_true",
                        help="Lists all users in the data store")

    args = parser.parse_args()

    load_dotenv(dotenv_path=THIS_FILE_DIR.parent / ".env")
    check_environment_vars_setup()

    logging.basicConfig()

    conn, sess = create_connections_and_test()
    # We can safely assume if we reached this part that the connections
    # are stable. Well, assume because *something* might happen.
    if args.info:
        schemas = fetch_schemas(sess, env["KRATOS_ENDPOINT"])
        terminal.print_json(schemas)
    elif args.list:
        get_all_users(sess, env["KRATOS_ENDPOINT"])
    elif args.create:
        dummy_data_folder = THIS_FILE_DIR / "dev_dummy_data"
        seed_datastores(dummy_data_folder, conn, sess)
