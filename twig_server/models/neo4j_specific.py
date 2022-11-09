"""Some neo4j specific implementation details."""


class Neo4jId(int):
    """
    Neo4J id which happens to be an int.
    """

    pass


class RelationshipId(int):
    """
    A model for the ID of a relationship.

    Notes:
        This seems to be Neo4j specific.
    """

    pass


# class Neo4jRelationship(EdgeRelation[VK]):
#     id: Optional[RelationshipId]
