import enum
from typing import Optional, ClassVar, Generic

import neo4j.graph

from twig_server.models.types import VK


class Operation(enum.Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class CypherQueryString:
    def __init__(
        self,
        operation: Operation,
        *,
        returned_idx_name: Optional[str] = None,
        is_single: Optional[bool] = None,
        required_parameters: Optional[list[str]] = None,
        query_string: str,
    ):
        # TODO: Checks
        self.operation = operation
        self.required_parameters = required_parameters
        self.query_string = query_string
        self.is_single = is_single
        self.returned_idx_name = returned_idx_name

    def __str__(self):
        return self.query_string

    def execute(self, sess: neo4j.Session, parameters: Optional[dict] = None):
        # performs validation as well
        # Return the single thing if self.is_single otherwise it will return the result

        if self.required_parameters:
            if len(self.required_parameters) > 0 and parameters is None:
                raise ValueError("Parameters are required for this query.")
            if set(self.required_parameters) != set(parameters.keys()):
                raise ValueError(
                    f"Parameters {parameters.keys()} do not match"
                    f" required parameters {self.required_parameters}"
                )

        result = sess.run(self.query_string, parameters)
        if self.is_single:
            result = result.single()
            if not result:
                raise Exception("A more concrete exception would be nice")
            return result[self.returned_idx_name]
        else:
            return result


class TwigNeoModel(Generic[VK]):
    __label_name__: ClassVar[str]

    # TODO: Figure out how to just execute it and not return query strings.
    @classmethod
    def get_all(cls) -> CypherQueryString:
        return CypherQueryString(
            Operation.READ,
            returned_idx_name="n",
            is_single=False,
            query_string=f"MATCH (n:{cls.__label_name__}) RETURN n",
        )

    @classmethod
    def get(cls, obj_id: VK) -> CypherQueryString:
        query_string = (
            f"MATCH (n:{cls.__label_name__}) WHERE id(n)={obj_id} RETURN n"
        )
        return CypherQueryString(
            Operation.READ,
            returned_idx_name="n",
            is_single=True,
            query_string=query_string,
        )

    # TODO: Figure out how to make this a self, in particular, the
    #  parameters should be automatically filled in for you in this case.
    @classmethod
    def create(cls):
        """Requires you to fill in props"""
        query_string = (
            f"CREATE (n:{cls.__label_name__}) SET n = $props RETURN id(n)"
        )
        return CypherQueryString(
            Operation.CREATE,
            returned_idx_name="id(n)",
            is_single=True,
            required_parameters=["props"],
            query_string=query_string,
        )

    # TODO: Figure out how to make this a self, in particular, the
    #  parameters should be automatically filled in for you in this case.
    @classmethod
    def update(cls):
        """Requires you to fill in new_data"""
        # TODO: Do a proper cypher update.
        # https://neo4j.com/developer/cypher/updating/#cypher-update
        query_string = f"""
        MATCH (n:{cls.__label_name__})
        WHERE id(n)=$id
        SET n = $props
        RETURN id(n) 
        """
        return CypherQueryString(
            Operation.UPDATE,
            returned_idx_name="id(n)",
            is_single=True,
            required_parameters=["new_data"],
            query_string=query_string,
        )

    # TODO: Figure out how to make this a self, in particular, the
    #  parameters should be automatically filled in for you in this case.
    @classmethod
    def delete(cls):
        """Requires you to fill in id"""
        query_string = f"""
        MATCH (n:{cls.__label_name__})
        WHERE id(n)=$id
        DETACH DELETE n
        """
        return CypherQueryString(
            Operation.DELETE,
            required_parameters=["id"],
            query_string=query_string,
        )


