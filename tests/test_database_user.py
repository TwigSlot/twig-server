from twig_server.database.User import User
import pytest


@pytest.fixture()
def create_user_username(connection):
    jh = User(connection, username="jh") # creating a user needs a username
    assert jh != None
    assert jh.dbObj == None 
    dbObj = jh.create()
    assert dbObj != None
    assert jh.dbObj != None
    assert dbObj == jh.dbObj
    yield jh
    jh.delete()

def test_database_create_user_username(create_user_username):
    assert create_user_username != None

def test_database_user_query_username(create_user_username):
    assert 'username' in create_user_username.properties
    assert create_user_username.properties['username'] != None
    assert type(create_user_username.properties['username']) is str
    assert create_user_username.query_username() != None

def test_database_user_get_uid(create_user_username):
    assert 'uid' in create_user_username.properties
    assert create_user_username.properties['uid'] != None
    assert type(create_user_username.properties['uid']) is int

def test_database_duplicate_username(connection, create_user_username):
    username = create_user_username.properties['username']
    dup = User(connection, username=username)
    assert dup.properties == create_user_username.properties

@pytest.fixture
def query_user_uid(connection, create_user_username):
    uid = create_user_username.properties['uid']
    user = User(connection, uid=uid)
    yield user
    user.delete()

def test_database_query_user_uid(query_user_uid, create_user_username):
    assert query_user_uid.properties == create_user_username.properties