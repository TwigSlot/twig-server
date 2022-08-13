from twig_server.database.User import User
from twig_server.neo4j import neo4j_driver


def test_driver_connectivity():
    neo4j_driver.verify_connectivity()


def test_database_user_query_username():
    tch = User("Tan Chien Hao")
    tch.query_username()


def test_database_user_create_and_delete():
    username = "chien hao"
    tch = User(username)
    tch.delete_username()
    assert tch.query_username() == None
    tch.create()
    assert tch.query_username()._properties["username"] == username
    tch.delete_username()
    assert tch.query_username() == None
