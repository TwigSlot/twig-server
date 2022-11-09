from twig_server.models import ResourceId, ProjectId


class CreationFailure(Exception):
    def __init__(self, label: str, obj: object):
        self.label = label
        self.obj = obj

    def __str__(self):
        return f"Failed to create object {self.obj} (label: {self.label})"


class ResourceNotFound(Exception):
    def __init__(self, resource_id: ResourceId):
        self.resource_id = resource_id
        super().__init__(f"Resource {resource_id} not found")


class ProjectNotFound(Exception):
    def __init__(self, project_id: ProjectId):
        self.project_id = project_id
        super().__init__(f"Project {project_id} not found")
