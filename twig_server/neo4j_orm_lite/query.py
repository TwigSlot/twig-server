"""Contains components for a sort of query-building system? Nothing is stable yet."""
import enum
from typing import Optional, Union

import neo4j


class Operation(enum.Enum):
    # Note: these strings are not actually used to generate the query string
    CREATE = "CREATE"
    MATCH = "MATCH"
    UPDATE_OVERWRITE = "UPDATE"
    DELETE = "DELETE"


class CypherQueryString:
    def __init__(
            self,
            operation: Operation,
            *,
            label_name: Optional[str] = None,
            returned_idx_name: Optional[str] = None,
            returned_idx_type: Optional[type] = None,
            is_single: Optional[bool] = None,
            required_parameters: Optional[list[tuple[str, type]]] = None, # todo: change this to a dict
            query_string: str,
    ):
        self.label_name = label_name
        self.operation = operation
        self.required_parameters = required_parameters
        self.is_single = is_single
        self.returned_idx_name = returned_idx_name
        self.returned_idx_type = returned_idx_type
        # clean up spaces
        self.query_string = ' '.join(query_string.split())

    def __str__(self):
        return self.query_string


class PreparedCypherQuery:
    """A Cypher Query that is ready to be executed, with the parameters filled in."""

    def __init__(self, query_string: CypherQueryString, parameters: Optional[dict] = None):
        # TODO: parameter and query validation
        self.query_string = query_string
        self.parameters = parameters

    def execute(self, sess: neo4j.Session) -> Union[neo4j.Record, neo4j.Result]:
        result = sess.run(str(self.query_string), self.parameters)
        if result.peek() is None:
            # TODO: A more concrete exception would be nice
            raise Exception("This query returned no results.")
        if self.query_string.is_single:
            result = result.single()
            # Note: we have no way to find out if there is more than one result
            # the only way to do this is with neo4j driver 5.0+
            return result[self.query_string.returned_idx_name]
        else:
            return result
