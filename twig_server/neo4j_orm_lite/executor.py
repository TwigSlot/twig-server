import warnings
from typing import Optional
from uuid import UUID

from twig_server.models import (
    Project,
    Resource,
    ProjectId,
    ResourceGraph,
    ResourceId,
)
from twig_server.neo4j_orm_lite.query import CypherQueryString, Operation


# TODO: This does NOT work at ALL
class HelperStuff:
    """
    Some helper stuff
    """

    def get_projects_accessible_to_user(
        self, user_id: UUID
    ) -> Optional[list[Project]]:
        """
        Retrieves all the projects accessible to a user. These projects can
        be edited by the user.

        A user can access a project if and only if they are the owner,
        or they have been added as a collaborator.

        Args:
            user_id: The user's ID. This is provided by Kratos, our identity provider.

        Returns:
            A list of projects will be returned if and only if
            the user has access to a nonzero number of projects.

        Raises:
            Might raise if we could not connect to Neo4j, I suppose.
            TODO: Figure out when this raises

        Notes:
            This will NOT populate the project's resources.
            TODO: We should make it easier to do that.
        """

        # TODO: Pull this from our permissions table

        # Note: it is safe to assume this is a set, and only has unique values
        projects_user_has_access_to: list[int] = []

        # This query filters to ensure we only pull project nodes
        # and the node has id which is in the list of projects the user has access to

        # Note: Project is capital to avoid a migration
        query_string = f"""
        MATCH (p:Project)
        WHERE id(p) IN $projects_user_has_access_to
        RETURN p
        """
        cq = CypherQueryString(
            Operation.MATCH,
            returned_idx_name="p",
            is_single=False,
            required_parameters=[("projects_user_has_access_to", list[int])],
            query_string=query_string,
        )
        ret_val = self.execute_and_convert(cq, Project)
        return ret_val if len(ret_val) > 0 else None

    def get_resources(self, project_id: ProjectId) -> ResourceGraph:
        """
        Retrieves all the resources in a project.

        Args:
            project_id: The ID of the project to retrieve resources from.

        Returns:
            A ResourceGraph object

        Raises:
            ProjectNotFound: If the project was not found.
        """

        # We need to pull out the relationships between the resources too
        # so we can build the models

        # TODO: Check if the project exists.
        #  Is there any way to do this in a SINGLE query?

        vertices_query_string = """
        MATCH (p:project)-[:has_resource]->(r:resource)
        WHERE id(p) = $project_id
        RETURN r
        """

        # Is it inefficient to leave in p, r1 and r2 when I'm not extracting them?
        edges_query_string = """
        MATCH (p:project)-[:has_resource]->(r1:resource)-[pr:prereq]->(r2:resource)
        WHERE id(p) = $project_id
        RETURN pr
        """
        with self.conn.session() as sess:
            vertices = sess.run(
                vertices_query_string, {"project_id": project_id}
            )
            edges = sess.run(edges_query_string, {"project_id": project_id})

            # TODO: This dictionary comprehension should be hidden away in a converter
            vertex_set = {
                ResourceId(vertex["r"].id): Resource(
                    id=ResourceId(vertex["r"].id), **dict(vertex["r"].items())
                )
                for vertex in vertices
            }
            if len(vertex_set) == 0:
                warnings.warn(
                    "Refactor the Graph type to support empty graphs properly"
                )

            # TODO: Hide this away too
            edge_set = {
                (
                    ResourceId(edge["pr"].start_node.id),
                    ResourceId(edge["pr"].end_node.id),
                )
                for edge in edges
            }

            return_val = ResourceGraph(vertices=vertex_set, edges=edge_set)
            return return_val
