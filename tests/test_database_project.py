import pytest

from twig_server.database.Project import Project


@pytest.fixture()
def create_project(connection, create_user_username):
    name = "my first project"
    proj = Project(connection, name)
    owner = create_user_username
    proj.create(owner)
    assert proj.dbObj != None
    yield proj
    proj.delete()


def test_database_create_project(create_project):
    assert create_project != None


def test_database_project_query_uid(create_project):
    assert create_project.query_uid() != None
