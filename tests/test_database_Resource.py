from dotenv import load_dotenv
load_dotenv()

from twig_server.database.Resource import Resource

def test_resource_create():
    resource = Resource(123)
    print(resource)