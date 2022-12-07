from flask import Blueprint


# API Endpoint: /resources
resources_router = Blueprint("resources", __name__)


@resources_router.get("/<resource_id:int>")
def get_resource(resource_id: int):
    """API Endpoint to retrieve a singular resource"""
    pass


@resources_router.get("/under-project/<project_id:int>")
def get_resources_under_project(project_id: int):
    """API Endpoint to retrieve all resources under a project"""
    pass


@resources_router.post("/")
def create_resource():
    """
    API Endpoint to create a resource

    Notes:
        The implementor should take the project_id
        and other necessary details from the request body

        Tags should not be created here, rather, the client is
        responsible for making an API call to create the
        tags beforehand, before associating them with this resource.
    """
    pass


@resources_router.delete("/<resource_id:int>")
def delete_resource(resource_id: int):
    """API Endpoint to delete a resource"""
    pass


@resources_router.put("/<resource_id:int>")
def update_resource(resource_id: int):
    """
    API Endpoint to update a resource

    Notes:

    """
    pass
