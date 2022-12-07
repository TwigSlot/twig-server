from flask import Blueprint

# API Base url: /project
project_router = Blueprint("projects", __name__)


@project_router.post("/")
def create_project():
    """
    API Endpoint to create a new project
    """
    pass


@project_router.get("/<project_id:int>")
def get_project(project_id: int):
    """
    API endpoint to retrieve a project with all of its resources and tags.

    Notes:
        The above behavior may be subject to change.
    """
    pass


@project_router.delete("/<project_id:int>")
def delete_project(project_id: int):
    """
    API Endpoint to delete a project
    (including all resources associated with the project)"""
    pass


@project_router.put("/<project_id:int>")
def update_project_metadata(project_id: int):
    """
    API Endpoint to update a project metadata.
    To update the resources or tags, see the other endpoints

    Args:
        project_id: Self-explanatory

    """
    pass
