from twig_server.database.Native import Node
from twig_server.database.User import User


class Project(Node):
    _label_name = "Project"

    def __init__(self, conn, uid=None, name="Untitled Project", owner=None):
        super().__init__(conn, uid)
        self.name = name
        self.owner: User = owner

    def set_owner(self, owner):
        self.owner = owner

    def create(self, owner):
        super().create(Project._label_name)
        self.set_owner(owner)
