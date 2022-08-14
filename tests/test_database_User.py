from twig_server.database.User import User
from twig_server.database.connection import Neo4jConnection
import pytest


@pytest.mark.skip()
def test_database_user_query_username():
    tch = User("Tan Chien Hao")
    tch.query_username()


@pytest.mark.skip()
def test_database_user_create_and_delete():
    username = "chien hao"
    tch = User(username)
    tch.delete_username()
    assert tch.query_username() == None
    tch.create()
    assert tch.query_username()._properties["username"] == username
    tch.delete_username()
    assert tch.query_username() == None
