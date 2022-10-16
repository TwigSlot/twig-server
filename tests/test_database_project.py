import pytest

from twig_server.database.Project import Project
from twig_server.database.connection import Neo4jConnection, Neo4jDriver


@pytest.fixture()
def create_project(connection, create_user_username):
    name = "my first project"
    proj = Project(connection, name=name)
    owner = create_user_username
    proj.create(owner)
    assert proj.db_obj is not None
    yield proj
    proj.delete()


def test_database_create_project(create_project):
    assert create_project is not None


def test_database_project_query_uid(create_project):
    assert create_project.query_uid() is not None


def test_database_project_ownership(create_project):
    assert create_project.owner_rls is not None


def test_database_list_projects(
    connection: Neo4jDriver, create_project: Project
):
    assert (
        len(Project.list_projects(connection.conn, create_project.owner)) == 1
    )
