from abc import ABC


class AbstractNode(ABC):
    def __init__(self):
        pass


class AbstractEdge(ABC):
    """
    An abstract directed edge between 2 nodes.
    """

    def __init__(self, src: AbstractNode, dst: AbstractNode):
        self.src = src
        self.dst = dst
