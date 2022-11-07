import json
from typing import Optional
from uuid import UUID

import executing
from neo4j import Neo4jDriver
from pydantic import BaseModel

from twig_server.database.graph.twigslot_objects import (
    Project,
    Resource,
    ProjectId,
    ResourceId,
    ResourceRelationships,
    ResourceGraph,
    RelationshipId,
)


# TODO: Move exceptions into another file


class CreationFailure(Exception):
    pass


class ResourceNotFound(Exception):
    pass


class ProjectNotFound(Exception):
    pass


class RawNeo4jBacking:
    """Some low level functions for *most* C, U, D operations"""

    def __init__(self, conn: Neo4jDriver):
        self.conn = conn

    def create(self, label: str, obj: dict) -> Optional[int]:
        """Inserts a new object into the database"""
        insert_query = f"CREATE (n:{label}) SET n = $props RETURN id(n)"

        with self.conn.session() as session:
            # TODO: Wait, can we just do this?
            res = session.run(insert_query, parameters={"props": obj})
            res = res.single()
            if res:
                return res[0]["id(n)"]
            else:
                return None

    def update(self, label: str, obj_id: int, obj: dict):
        """
        Performs an update on an object in the database

        Notes:
            This is not a true incremental update. It will overwrite the entire
            object with the new object.
        """
        # TODO: Do a proper cypher update
        # https://neo4j.com/developer/cypher/updating/#cypher-update
        query_string = f"""
        MATCH (n:{label})
        WHERE id(n) = $obj_id
        SET n = $new_data
        """
        with self.conn.session() as session:
            session.run(
                query_string, parameters={"obj_id": obj_id, "new_data": obj}
            )

    def delete(self, label: str, obj_id: int):
        """Deletes an object from the database. This will delete all relationships"""
        query_string = f"""
        MATCH (n:{label})
        WHERE id(n) = $obj_id
        DETACH DELETE n
        """
        # TODO: We should probably raise an exception if the object doesn't exist?
        with self.conn.session() as session:
            session.run(query_string, parameters={"obj_id": obj_id})


class Twig4jOrm:
    """
    A simple Neo4j ORM for Twig.

    Notes:
        There are some horrible practices here, TODO: fix that.

    """

    def __init__(self, conn: Neo4jDriver):
        # Note: assumes that connection is already established!
        self.conn = conn
        self.raw_backing = RawNeo4jBacking(conn)

    def get_all_projects(self) -> list[Project]:
        """
        Retrieves all the projects we currently have stored.

        This is most useful for the "explore projects" page,
        where we want to show all the projects we have.

        Notes:
            Not sure how awful the performance would be if we
            do this, actually. We might want to paginate this.
            TODO: Figure out if we need to paginate this.

        Returns:
            A list of projects will be returned if and only if
            there are nonzero projects in the database.
        """
        query_string = """
        MATCH (p:project)
        RETURN p
        """
        with self.conn.session() as sess:
            results = sess.run(query_string)
            return_val = list(
                map(
                    lambda record: Project(
                        id=record["p"].id,
                        # Note: record['p'].items() is a dict_keys
                        # not a dict, so this is needed
                        **dict(record["p"].items()),
                    ),
                    results,
                )
            )
            return return_val

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
        with self.conn.session() as sess:
            results = sess.run(
                query_string,
                {"projects_user_has_access_to": projects_user_has_access_to},
            )
            # TODO: Check if this actually works
            return_val = list(
                map(
                    # in particular, this line. What is `record`?
                    lambda record: Project(**record),
                    results,
                )
            )
            return return_val if len(return_val) > 0 else None

    def get_project(self, project_id: ProjectId) -> Optional[Project]:
        """
        Retrieves a project by its neo4j ID.

        Args:
            project_id: The ID of the project to retrieve.

        Returns:
            The project if it exists, None otherwise.

        Notes:
            The project returned by this will have `None` for its
            resources. You will need to fill this in manually with
            :py:meth:`Neo4jOrm.get_resources`.
        """
        # TODO: There is some duplication here, this can probably be combined with
        # get_projects_accessible_to_user
        query_string = """
        MATCH (p:project)
        WHERE id(p) = $project_id
        RETURN p
        """
        with self.conn.session() as sess:
            result = sess.run(query_string, {"project_id": project_id})
            # Note: We are assuming that the result is certainly a single object
            # If you see a warning, it sounds like a neo4j bug, since the id
            # should be a unique mapping to a single neo4j node
            result = result.single()[0]

            return (
                Project(id=result.id, **dict(result.items()))
                if result
                else None
            )

    def create_project(self, project: Project) -> ProjectId:
        """
        Creates a new project in the database.

        Notes:
            TODO: I should probably raise if the project already exists

        Args:
            project: The project to create.

        Returns:
            The ID of the newly created project.

        Raises:
            CreationFailure: If the project could not be created.
        """

        out = self.raw_backing.create("project", json.loads(project.json()))
        if out is None:
            raise CreationFailure("Could not create project")
        return ProjectId(out)

    def update_project(self, project_id: ProjectId, new_data: Project) -> None:
        """
        Updates a project in the database.

        Args:
            project_id: The ID of the project to update.
            new_data: The new data to update the project with.

        Notes:
            This is extremely low level and will happily update the project even
            if you change the following properties:
            - owner

        Notes:
            You are expected to change your own modification_time.

        """

        # TODO: Do a proper cypher update
        # https://neo4j.com/developer/cypher/updating/#cypher-update
        self.raw_backing.update(
            "project",
            project_id,
            json.loads(new_data.json(exclude={"id", "resources"})),
        )

    def delete_project(self, project_id: ProjectId) -> None:
        """
        Deletes a project from the database.

        Args:
            project_id: The ID of the project to delete.
        """
        self.raw_backing.delete("project", project_id)

    def get_resources(self, project_id: ProjectId) -> Optional[ResourceGraph]:
        """
        Retrieves all the resources in a project.

        Args:
            project_id: The ID of the project to retrieve resources from.

        Returns:
            A ResourceGraph object if the project exists, None otherwise.
        """

        # We need to pull out the relationships between the resources too
        # so we can build the graph

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
                return None

            # TODO: Hide this away too
            edge_set = {
                (
                    ResourceId(edge["pr"].start_node.id),
                    ResourceId(edge["pr"].end_node.id),
                )
                for edge in edges
            }

            return_val = ResourceGraph.parse_obj(
                {"_vertices": vertex_set, "edges": edge_set}
            )
            return return_val

    def get_resource(self, resource_id: ResourceId) -> Resource:
        """
        Retrieves a resource with the id. This can retrieve a resource under any
        project.

        Args:
            resource_id: The id of the resource

        Returns:
            The resource

        Raises:
            :py:class:`ResourceNotFound` if the resource does not exist

        Notes:
            This makes no guarantee that the resource has not changed since it was
            retrieved. You could genuinely get a different resource with the same ID.
        """
        query_string = """
        MATCH (r:resource)
        WHERE id(r) = $resource_id
        RETURN r
        """
        with self.conn.session() as sess:
            results = sess.run(query_string, {"resource_id": resource_id})
            try:
                result = results.single()
                if result is None:
                    raise
                node = result["r"]
                return Resource(id=node.id, **dict(node.items()))
            except executing.NotOneValueFound:
                raise ResourceNotFound()
            except ResourceNotFound:
                raise ResourceNotFound(
                    f"Resource with id {resource_id} does not exist"
                )

    def create_resource(
        self,
        resource: Resource,
        project_id: ProjectId,
        relationships: Optional[ResourceRelationships] = None,
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
        """

        if relationships is not None:
            raise NotImplementedError(
                "Creating a resource with relationships is not yet implemented."
            )

        # TODO: Should we check for duplicate resources? How should we do that anyway?

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
                    "resource": json.loads(resource.json()),
                    "project_id": project_id,
                },
            )
            result = results.single()
            if result:
                return result["id(r)"]
            else:
                raise ProjectNotFound(
                    f"Project with id {project_id} does not exist"
                )

    def update_resource(
        self, resource_id: ResourceId, new_data: Resource
    ) -> None:
        """
        Updates a resource in the database.

        Args:
            resource_id: The ID of the resource to update.
            new_data: The new data to update the resource with.

        """
        self.raw_backing.update(
            "resource", resource_id, json.loads(new_data.json(exclude={"id"}))
        )

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
        query_string = """
        MATCH (src:resource), (dst:resource)
        WHERE id(src) = $src AND id(dst) = $dst
        CREATE (src)-[rs:prereq]->(dst)
        RETURN rs
        """
        with self.conn.session() as sess:
            result = sess.run(query_string, {"src": src, "dst": dst})
            if result:
                return result.single()["rs"].id

    def add_multiple_relationships(self, relationships: ResourceRelationships):
        raise NotImplementedError("Not implemented yet")

    def delete_resource(self, resource_id: ResourceId):
        """
        Deletes a resource with id

        Args:
            resource_id: The id of the resource

        Returns:
            None

        Raises:
            :py:class:`ResourceNotFound` if the resource does not exist
        """
        self.raw_backing.delete("resource", resource_id)
