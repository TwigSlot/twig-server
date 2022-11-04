import json
from typing import Optional
from uuid import UUID

from neo4j import Neo4jDriver

from twig_server.database.graph.neo4j_objects import Neo4jNode
from twig_server.database.graph.twigslot_objects import Project, Resource


# TODO: Move these into another file
class ResourceNotFound(Exception):
    pass


class ProjectNotFound(Exception):
    pass

class RawNeo4jBacking:
    def __init__(self, conn: Neo4jDriver):
        self.conn = conn

    def insert(self, obj: Neo4jNode) -> Optional[int]:
        """Inserts a new object into the database"""
        insert_labels = obj.labels
        insert_properties = obj.properties
        insert_query = f"CREATE (n:{insert_labels}) SET n = $props RETURN id(n)"

        with self.conn.session() as session:
            # TODO: Wait, can we just do this?
            res = session.run(insert_query, kwparameters=insert_properties)
            res = res.single()
            if res:
                return res[0]
            else:
                return None


class Neo4jOrm:
    """
    A simple Neo4j ORM for Twig.

    Notes:
        There are some horrible practices here, TODO: fix that.

    """

    def __init__(self, conn: Neo4jDriver):
        # Note: assumes that connection is already established!
        self.conn = conn

    def get_all_projects(self) -> Optional[list[Project]]:
        """
        Retrieves all the projects we currently have stored.

        This is most useful for the "explore projects" page,
        where we want to show all the projects we have.

        Notes:
            Not sure how awful the performance would be if we
            do this, actually. We might want to paginate this.
            TODO: Figure out if we need to paginate this.

        Notes:
            It's a bit pedantic to have Optional, since it's
            unlikely there will be NO projects at all.
            TODO: Don't be so pedantic.

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
            # TODO: Check if this actually works
            return_val = list(
                map(
                    # in particular, this line. What is `record`?
                    lambda record: Project(**record),
                    results,
                )
            )
            return return_val if len(return_val) > 0 else None

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

    def get_project(self, project_id: int) -> Optional[Project]:
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
            # TODO: Verify that this result actually only yields one object
            result = sess.run(query_string, {"project_id": project_id})
            result = result.single()

            return Project(**result) if result else None

    def create_project(self, project: Project) -> int:
        """
        Creates a new project in the database.

        Notes:
            TODO: I should probably raise if the project already exists

        Args:
            project: The project to create.

        Returns:
            The ID of the newly created project.
        """

        # TODO: Check this query string works
        query_string = """
        CREATE (p:project)
        SET p = $project
        RETURN id(p)
        """
        with self.conn.session() as sess:
            # TODO: Verify that this actually works
            result = sess.run(
                query_string,
                {
                    # TODO: Deserializing and reserializing like this could be expensive
                    "project": json.loads(project.json())
                },
            )
            return result.data()[0]["id(p)"]

    def update_project(self, project_id: int, new_data: Project) -> None:
        """
        Updates a project in the database.

        Args:
            project_id: The ID of the project to update.
            new_data: The new data to update the project with.

        """

        # TODO: Check this query string works
        query_string = """
        MATCH (p:project)
        WHERE id(p) = $project_id
        SET p = $new_data
        """
        with self.conn.session() as sess:
            sess.run(
                query_string,
                {
                    "project_id": project_id,
                    "new_data": json.loads(new_data.json()),
                },
            )

    def delete_project(self, project_id: int) -> None:
        """
        Deletes a project from the database.

        Args:
            project_id: The ID of the project to delete.
        """

        # TODO: Check this query string works
        query_string = """
        MATCH (p:project)
        WHERE id(p) = $project_id
        DETACH DELETE p
        """
        with self.conn.session() as sess:
            sess.run(query_string, {"project_id": project_id})

    def get_resources(self, project_id: int) -> Optional[list[Resource]]:
        """
        Retrieves all the resources in a project.

        Args:
            project_id: The ID of the project to retrieve resources from.

        Returns:
            A list of resources if the project exists, None otherwise.
        """

        # TODO: Check this query string works
        query_string = """
        MATCH (p:Project)-[:Has_Resource]->(r:resource)
        WHERE id(p) = $project_id
        RETURN r
        """
        with self.conn.session() as sess:
            results = sess.run(query_string, {"project_id": project_id})
            return_val = list(
                map(
                    # in particular, this line. What is `record`?
                    lambda record: Resource(**record),
                    results,
                )
            )
            return return_val if len(return_val) > 0 else None

    def get_resource(self, resource_id: int) -> Resource:
        """
        Retrieves a resource with the id

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

        # TODO: Check this query string works
        # TODO: Check if this can be combined with get_resources to reduce duplications
        #  maybe like a private method or something.
        query_string = """
        MATCH (r:resource)
        WHERE id(r) = $resource_id
        RETURN r
        """
        with self.conn.session() as sess:
            results = sess.run(query_string, {"resource_id": resource_id})
            result = results.single()
            if result:
                return Resource(**result)
            else:
                raise ResourceNotFound(
                    f"Resource with id {resource_id} does not exist"
                )

    def create_resource(self, resource: Resource, project_id: int) -> int:
        """
        Creates a new resource in Neo4j

        Args:
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

        # TODO: Should we check for duplicate resources? How should we do that anyway?
        # TODO: Check this query string works

        query_string = """
        MATCH (p:project)
        WHERE id(p) = $project_id
        CREATE (p)-[:Has_Resource]->(r:resource)
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

    def update_resource(self, resource_id: int, new_data: Resource) -> None:
        """
        Updates a resource in the database.

        Args:
            resource_id: The ID of the resource to update.
            new_data: The new data to update the resource with.

        """
        # TODO: Check this query string works
        query_string = """
        MATCH (r:resource)
        WHERE id(r) = $resource_id
        SET r = $new_data
        """
        with self.conn.session() as sess:
            sess.run(
                query_string,
                {
                    "resource_id": resource_id,
                    "new_data": json.loads(new_data.json()),
                },
            )

    def delete_resource(self, resource_id: int):
        """
        Deletes a resource with id

        Args:
            resource_id: The id of the resource

        Returns:
            None

        Raises:
            :py:class:`ResourceNotFound` if the resource does not exist
        """

        # TODO: Check this query string works
        query_string = """
        MATCH (r:resource)
        WHERE id(r) = $resource_id
        DETACH DELETE r
        """
        with self.conn.session() as sess:
            results = sess.run(query_string, {"resource_id": resource_id})
            if results.single() is None:
                raise ResourceNotFound(
                    f"Resource with id {resource_id} does not exist"
                )
