from typing import Mapping, Any

from pydantic import BaseModel


class Neo4jNode(BaseModel):
    id: int  # The ID of the node in Neo4J
    labels: list
    properties: Mapping[str, Any]


class Neo4jRelationship(BaseModel):
    id: int  # The ID of the relationship in Neo4J
    type: str
    src_id: str
    dst_id: str
    properties: Mapping[str, Any]
