from sqlite3 import connect
from twig_server.database.Resource import Resource
import pytest


@pytest.fixture
def create_resource(connection):
    # create locally
    resource = Resource(
        connection
    )  # passing in empty UID means we are interested in creating
    assert resource != None
    assert resource.dbObj == None
    assert "uid" not in resource.properties
    # sync with db
    dbObj = resource.create()
    assert dbObj != None
    assert resource.dbObj != None
    assert resource.dbObj == dbObj
    assert "uid" in resource.properties
    yield resource
    # clean up in db
    uid = resource.properties["uid"]
    assert uid != None
    resource.delete()
    assert "uid" not in resource.properties
    assert resource.dbObj == None

    assert Resource(connection, uid).query_uid() == None


def test_create_resource(create_resource : Resource):
    assert create_resource != None


def test_resource_query(create_resource : Resource):
    assert create_resource.query_uid() != None


def test_resource_query_uid(connection, create_resource):
    uid = create_resource.properties["uid"]
    assert Resource(connection, uid) != None


def test_resource_query_uid_not_found(connection):
    assert Resource(connection, 123901924091023902).dbObj == None
    assert Resource(connection, 123901924091023902).properties == {}
