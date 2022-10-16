import logging
from os import environ as env
import argparse
import pathlib
from typing import Optional

import requests
import urllib3
import yaml
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from rich.progress import track

from dotenv import load_dotenv
from yaml import Loader

from tools.network_functions import (
    fetch_schemas,
    get_all_users,
    create_user,
    delete_user_from_kratos,
    delete_user_from_neo4j,
)
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


def seed_users(
    neo4j_conn: Neo4jConnection,
    session: requests.Session,
    users: list[dict],
    *,
    logger: logging.Logger,
    console: Optional[Console] = None,
) -> tuple[list[User], list[tuple[User, str]]]:
    """
    Seeds all the users into the database.

    Notes:
        Currently due to non-optimal factoring this also actually requires us
        to insert the users into the Neo4j database. Future work by tch (or me) will
        eliminate this dependency.

    Args:
        users: List of users in the proper format
        neo4j_conn: The neo4j connection
        session: The requests session
        logger: a logger for us to send logging information into.
        console: Optionally, the rich console to use for printing if you are using
                this from a CLI program.

    Returns:
        A tuple. The first element is the list of all users that were created
        successfully. The second element is a list of tuples, where the first
        element is the user that failed to be created, and the second element
        is the error message.

    Raises:
        Will raise if we cannot connect to any of the data stores.
        Will also raise if we encounter a non-success HTTP response code
        when attempting to perform any operation.
    """
    users_list = User.deserialize_all(users)
    successful = []
    failed = []
    if console is not None:
        # probably a minimal performance improvement but whatever.
        logger.debug("Will output progress bar")
        user_iterator = track(
            users_list,
            description="[bold green]Creating users[/bold green]",
            console=console,
        )
    else:
        user_iterator = users_list

    for user in user_iterator:
        logger.debug(f"Attempting to create user {user.username}")
        creation_resp = create_user(
            user, admin_endpoint=env["KRATOS_ADMIN_ENDPOINT"], sess=session
        )
        if creation_resp.status_code == 201:
            kratos_id = creation_resp.json()["id"]
            user.kratos_id = kratos_id
            # TODO: gotta handle if this fails!
            user.to_twig_user(neo4j_conn).create()
            successful.append(user)
        else:
            logger.debug(
                f"[bold red]Failed creating user: [cyan]{user.username}[/cyan]"
                f"[/bold red]"
            )
            logger.debug(creation_resp.json())
            failed.append((user, creation_resp.text))
    return successful, failed


def create_connections_and_test(
    logger: logging.Logger,
) -> tuple[Neo4jConnection, requests.Session]:
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
        logger.error(
            "Looks like we could not connect to Neo4j. "
            "Please check if it is running!"
        )
        raise e

    # test kratos endpoints
    try:
        sess.get(env["KRATOS_ENDPOINT"] + "/health/alive").raise_for_status()
    except requests.HTTPError as e:
        logger.error(
            "Looks like we could not connect to Kratos. "
            "Please check if it is running!"
        )
        raise e
    return neo4j_connection, sess


def seed_datastores(
    dev_data_folder: pathlib.Path,
    neo4j_conn: Neo4jConnection,
    session: requests.Session,
    console: Console,
    logging_logger: logging.Logger,
):
    """
    Fully seed all datastores.

    This will seed Kratos with some development users, and Neo4j with
    some projects associated with those development users

    Notes:
        This function is not meant to be executed except in a CLI program.
        It should be evident from the fact that I'm requesting for a rich console.

    Args:
        dev_data_folder: The folder which contains the dummy data.
                        Should be named `dev_dummy_data`
        neo4j_conn: The Neo4j connection to use
        session: The requests session to use
        console: The rich console to use for printing
        logging_logger: Logger for us to send logging information into.

    Returns:
        Tuple of (successfully_created_users, unsuccessfully_created_users)

    Raises:
        Will raise if we cannot connect to any of the datastores.
    """
    with open(dev_data_folder / "users.yml", "r") as users_file:
        users = yaml.load(users_file, Loader=Loader)

        user_deets = Table(title="User information")
        user_deets.add_column("Username", style="cyan")
        user_deets.add_column("Password", style="green")
        user_deets.add_column("Kratos ID", style="magenta")

        failed_creations = Table(title="Failed users")
        failed_creations.add_column("Username", style="red")
        failed_creations.add_column("Error message")

        successful, failed = seed_users(
            neo4j_conn, session, users, logger=logging_logger, console=console
        )
        # TODO: Don't bother printing out successful users
        for user in successful:
            user_deets.add_row(user.username, user.password, user.kratos_id)
        for user, error in failed:
            failed_creations.add_row(user.username, error)

    if user_deets.row_count > 0:
        console.print(user_deets)
    if failed_creations.row_count > 0:
        console.print(failed_creations)


if __name__ == "__main__":
    THIS_FILE_DIR = pathlib.Path(__file__).parent.resolve()
    terminal = Console()

    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "-i",
        "--info",
        action="store_true",
        help="Pretty-print the Kratos identity schema",
    )
    action.add_argument(
        "-c",
        "--create",
        action="store_true",
        help="Seeds all data stores with dummy data, creating all the "
        "users projects and resources",
    )
    action.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Purges all data from the data stores",
    )
    action.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="Lists all users in the data store",
    )

    args = parser.parse_args()

    load_dotenv(dotenv_path=THIS_FILE_DIR.parent / ".env")
    check_environment_vars_setup()

    logging.basicConfig(
        handlers=[RichHandler(markup=True, tracebacks_suppress=[urllib3])]
    )
    logger = logging.getLogger("dev_seed")

    conn, sess = create_connections_and_test(logger)
    # We can safely assume if we reached this part that the connections
    # are stable. Well, assume because *something* might happen.
    if args.info:
        terminal.rule("Kratos identity schema")
        schemas = fetch_schemas(sess, env["KRATOS_ENDPOINT"])
        terminal.print_json(data=schemas)
        terminal.rule("End identity schema info")
    elif args.list:
        terminal.rule("Listing all users")
        all_users = User.from_kratos_schemas(
            get_all_users(sess, env["KRATOS_ADMIN_ENDPOINT"])
        )
        user_deets = Table(title="User information")
        user_deets.add_column("Kratos ID", style="magenta")
        user_deets.add_column("Username/Email", style="cyan")
        user_deets.add_column("First name", style="green")
        user_deets.add_column("Last name", style="green")
        for user in all_users:
            user_deets.add_row(
                user.kratos_id, user.username, user.first_name, user.last_name
            )
        if user_deets.row_count > 0:
            terminal.print(user_deets)
        terminal.rule("End listing all users")
    elif args.create:
        dummy_data_folder = THIS_FILE_DIR / "dev_dummy_data"
        seed_datastores(dummy_data_folder, conn, sess, terminal, logger)
    elif args.delete:
        terminal.print(
            "[bold red]Deleting all users from datastores[/bold red]"
        )
        all_users = User.from_kratos_schemas(
            get_all_users(sess, env["KRATOS_ADMIN_ENDPOINT"])
        )
        for user in track(all_users, description="Deleting users"):
            # Note: I have assumed that the user has a kratos id!
            # This is a "safe" assumption in this case, but not in general.
            delete_user_from_kratos(
                user.kratos_id, sess, env["KRATOS_ADMIN_ENDPOINT"]
            )
            delete_user_from_neo4j(user.kratos_id, conn)
