# from sqlite3 import connect
# from twig_server.database.Resource import Resource
# import pytest


# @pytest.fixture
# def create_resource(connection):
#     # create locally
#     resource = Resource(
#         connection
#     )  # passing in empty UID means we are interested in creating
#     assert resource != None
#     assert resource.db_obj == None
#     assert "uid" not in resource.properties
#     # sync with db
#     db_obj = resource.create()
#     assert db_obj != None
#     assert resource.db_obj != None
#     assert resource.db_obj == db_obj
#     assert "uid" in resource.properties
#     yield resource
#     # clean up in db
#     uid = resource.properties["uid"]
#     assert uid != None
#     resource.delete()
#     assert "uid" not in resource.properties
#     assert resource.db_obj == None

#     assert Resource(connection, uid).query_uid() == None


# def test_create_resource(create_resource):
#     assert create_resource != None


# def test_resource_query(create_resource):
#     assert create_resource.query_uid() != None


# def test_resource_query_uid(connection, create_resource):
#     uid = create_resource.properties["uid"]
#     assert Resource(connection, uid) != None


# def test_resource_query_uid_not_found(connection):
#     assert Resource(connection, 123901924091023902).db_obj == None
#     assert Resource(connection, 123901924091023902).properties == {}
