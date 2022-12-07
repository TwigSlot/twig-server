from flask import Blueprint


# API Endpoint: /tags

tags_router = Blueprint("tags", __name__)


@tags_router.get("/<tag_id:int>")
def get_tag(tag_id: int):
    """API Endpoint to retrieve a singular tag"""
    pass


@tags_router.get("/under-project/<project_id:int>")
def get_tags_under_project(project_id: int):
    """API Endpoint to retrieve that a project contains"""
    pass


@tags_router.post("/")
def create_tag():
    """
    API Endpoint to create a tag
    """
    pass


@tags_router.delete("/<tag_id:int>")
def delete_tag(tag_id: int):
    """API Endpoint to delete a tag"""
    pass

