import uuid

import pytest

from twig_server.models import Project, Resource
from twig_server.neo4j_orm_lite.orm import TwigORMSession


# TODO: All these tests need to be CLEANED UP OMG


@pytest.mark.parametrize(
    "name,description,owner",
    [
        (f"test_proj_{n}", f"test_proj_desc_{n}", uuid.uuid4())
        for n in range(10)
    ],
)
def test_create_project(neo4j_server, name, description, owner):
    with TwigORMSession(neo4j_server) as sess:
        proj = Project(name=name, description=description, owner=owner)
        sess.add(proj)
        print(sess.show_query())
        proj_id = sess.commit()
        proj_id = proj_id[0]
        assert proj_id is not None
        proj_get = sess.get(proj_id)
        assert isinstance(proj_get, Project)

    #
    # del_query = proj.delete()
    # with twig4j_orm.conn.session() as sess:
    #     del_query.execute(sess, {"id": proj_id})


@pytest.mark.parametrize(
    "project,resources",
    [
        (
            Project(
                name=f"test_proj_{n}",
                description=f"test_proj_desc_{n}",
                owner=uuid.uuid4(),
            ),
            [
                Resource(
                    name=f"test_res_{n}",
                    description=f"test_res_desc_{n}",
                    url="https://www.google.com",
                )
                for n in range(10)
            ],
        )
        for n in range(2)
    ],
)
def test_create_resource(neo4j_server, project, resources):
    with TwigORMSession(neo4j_server) as sess:
        project.add_resources(resources)
        sess.add(project)
        sess.commit()