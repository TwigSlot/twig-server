from flask import current_app, request

from twig_server.database.Project import Project
from twig_server.database.Resource import Resource
from twig_server.database.Tag import Tag


def authorize_user(project: Project):
    kratos_user_id = request.headers.get("X-User")
    owner = project.get_owner()
    if kratos_user_id != owner["kratos_user_id"]:
        return False
    return True


def tag_belongs_to_project(tag: Tag, project: Project):
    return int(tag.get_project_properties()["uid"]) == int(
        project.properties["uid"]
    )


def helper_get_project(project_id: str):
    project_uid = int(project_id)
    assert project_uid is not None
    project = Project(current_app.config["driver"], uid=project_uid)
    project.query_uid()
    assert project.db_obj is not None
    return project


def helper_get_resource(resource_id: str):
    resource_uid = int(resource_id)
    assert resource_uid is not None
    resource = Resource(current_app.config["driver"], uid=resource_uid)
    resource.query_uid()
    assert resource.db_obj is not None
    return resource


def helper_get_tag(tag_id: str):
    tag_uid = int(tag_id)
    assert tag_uid is not None
    tag = Tag(current_app.config["driver"], uid=tag_uid)
    tag.query_uid()
    assert tag.db_obj is not None
    return tag
