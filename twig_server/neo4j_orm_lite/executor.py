import warnings
from typing import Union, Type, Optional
from uuid import UUID

from neo4j import Neo4jDriver

from twig_server.models import (
    Project,
    Resource,
    Tag,
    ProjectId,
    ResourceGraph,
    ResourceId,
    EdgeRelation,
)
from twig_server.models.neo4j_specific import Neo4jId, RelationshipId
from twig_server.neo4j_orm_lite.exceptions import (
    CreationFailure,
    ProjectNotFound,
)
from twig_server.neo4j_orm_lite.orm import CypherQueryString, Operation


class CrappyNeo4jFakeOrm:
    """
    A fake and crappy Neo4j psuedo-ORM
    This provides some low level functions for *most* create, update, delete operations
    """

    def __init__(self, conn: Neo4jDriver):
        self.conn = conn

    def create_relationship(
        self,
        src: Neo4jId,
        src_label: str,
        dst: Neo4jId,
        dst_label: str,
        relationship_label: str,
    ) -> Neo4jId:
        """
        Constructs a directed relationship or edge between 2 vertices.

        TODO: Do we really need the label if we are using the ID?

        Args:
            src: The ID of the source vertex
            src_label: The label of the source vertex
            dst: The ID of the destination vertex
            dst_label: The label of the destination vertex
            relationship_label: The label of the relationship

        Returns:
            The ID of the relationship

        Raises:
            CreationFailure: If the relationship could not be created
        """
        query_string = f"""
        MATCH (src{':' + src_label if src_label else ''}),
        (dst{':' + dst_label if dst_label else ''})
        WHERE id(src) = $src_id AND id(dst) = $dst_id
        CREATE (src)-[r{':' + relationship_label if relationship_label else None}]->(
        dst)
        RETURN id(r)
        """
        with self.conn.session() as sess:
            result = sess.run(query_string, {"src": src, "dst": dst})
            result = result.single()
            # TODO: Does this check actually work?
            if result:
                return result[0]["id(r)"]
            else:
                raise CreationFailure(
                    relationship_label,
                    {
                        "src": src,
                        "src_label": src_label,
                        "dst": dst,
                        "dst_label": dst_label,
                    },
                )


class Twig4jOrm:
    """
    A simple Neo4j ORM for Twig.

    Notes:
        There are some horrible practices here, TODO: fix that.

    """

    def __init__(self, conn: Neo4jDriver):
        # Note: assumes that connection is already established!
        self.conn = conn
        self.raw_backing = CrappyNeo4jFakeOrm(conn)

    def execute_and_convert(
        self,
        query_string: CypherQueryString,
        desired_type: Union[Type[Project], Type[Resource], Type[Tag]],
        parameters: Optional[dict] = None,
    ) -> Union[
        Union[Project, list[Project]],
        Union[Resource, list[Resource]],
        Union[Tag, list[Tag]],
    ]:
        with self.conn.session() as sess:
            # TODO: Exception handling
            result = query_string.execute(sess, parameters)
            if query_string.is_single:
                return desired_type(id=result.id, **dict(result.items()))
            else:
                ret_val = []
                for record in result:
                    n = record[query_string.returned_idx_name]
                    ret_val.append(desired_type(id=n.id, **dict(n.items())))
                return ret_val

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
            Operation.READ,
            returned_idx_name="p",
            is_single=False,
            required_parameters=["projects_user_has_access_to"],
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

    def create_resource(
        self,
        resource: Resource,
        project_id: ProjectId,
        relationships: Optional[EdgeRelation] = None,
    ) -> ResourceId:
        """
        Creates a new resource in Neo4j

        Args:
            relationships: The relationships to create with the resource.
                Currently not implemented.
            resource: The resource to create
            project_id: The neo4j UID of the project to attach it to.

        Returns:
            The Neo4j UID of the resource newly created

        Raises:
            :py:class:`ProjectNotFound` if the project does not exist

        Notes:
            This method implicitly assumes that the user has
            access to the project. It does not check this.

        Notes:
            This will not try to stop you from inserting a duplicate resource.
            If you need to handle this, handle it at the API side.
        """

        if relationships is not None:
            raise NotImplementedError(
                "Creating a resource with relationships is not yet implemented."
            )

        query_string = """
        MATCH (p:project)
        WHERE id(p) = $project_id
        CREATE (p)-[:has_resource]->(r:resource)
        SET r = $resource
        RETURN id(r)
        """
        with self.conn.session() as sess:
            results = sess.run(
                query_string,
                {
                    "resource": resource.serialize_for_neo4j_insert(),
                    "project_id": project_id,
                },
            )
            result = results.single()
            if result:
                return result["id(r)"]
            else:
                raise ProjectNotFound(project_id)

    def add_relationship(
        self, src: ResourceId, dst: ResourceId
    ) -> RelationshipId:
        """
        Adds a relationship between 2 resources.
        This is a directed edge from `src` to `dst`

        Args:
            src: The source resource
            dst: The destination resource

        Returns:
            The ID of the relationship created
        """
        rs_id = self.raw_backing.create_relationship(
            src=src,
            src_label="resource",
            dst=dst,
            dst_label="resource",
            relationship_label="prereq",
        )
        return RelationshipId(rs_id)

    def add_multiple_relationships(self, relationships: EdgeRelation):
        raise NotImplementedError("Not implemented yet")
