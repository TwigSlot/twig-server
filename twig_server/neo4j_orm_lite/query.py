"""Contains components for a sort of query-building system? Nothing is stable yet."""
import enum
from typing import Optional

import neo4j

from twig_server.models.db_objects import BaseDbObject


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
        # TODO: This is horrible, cleanup this garbage
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


class CypherQuery:
    def __init__(self, query_string: CypherQueryString, obj: BaseDbObject):
        self.query_string = query_string
        self.obj = obj

    def execute(self, sess: neo4j.Session, parameters: Optional[dict] = None):
        result = self.query_string.execute(sess, parameters)
        if self.query_string.is_single:
            return self.obj.parse_obj(
                {"id": result.id, **dict(result.items())}
            )
        else:
            ret_val = []
            for record in result:
                n = record[self.query_string.returned_idx_name]
                ret_val.append(
                    self.obj.parse_obj({"id": n.id, **dict(n.items())})
                )
            return ret_val
