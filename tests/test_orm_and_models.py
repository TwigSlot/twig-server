import uuid

import pytest

from twig_server.models import Project, Resource


# TODO: All these tests need to be CLEANED UP OMG


@pytest.mark.parametrize(
    "name,description,owner",
    [
        (f"test_proj_{n}", f"test_proj_desc_{n}", uuid.uuid4())
        for n in range(10)
    ],
)
def test_create_project(twig4j_orm, name, description, owner):
    proj = Project(name=name, description=description, owner=owner)
    create_query = proj.create()
    with twig4j_orm.conn.session() as sess:
        proj_id = create_query.execute(
            sess, {"props": proj.serialize_for_neo4j_insert()}
        )
        assert proj_id

    get_query = proj.get(proj_id)
    proj_get = twig4j_orm.execute_and_convert(get_query, Project)
    assert (
        proj_get.serialize_for_neo4j_insert()
        == proj.serialize_for_neo4j_insert()
    )
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
def test_create_resource(twig4j_orm, project, resources):
    create_query = project.create()

    with twig4j_orm.conn.session() as sess:
        proj_id = create_query.execute(
            sess, {"props": project.serialize_for_neo4j_insert()}
        )
        assert proj_id
        resources_created = list(
            map(
                lambda res: twig4j_orm.create_resource(res, proj_id), resources
            )
        )
        assert len(resources_created) == len(resources)
        for i, res_id in enumerate(resources_created):
            res_get = twig4j_orm.execute_and_convert(
                Resource.get(res_id), Resource
            )
            assert (
                res_get.serialize_for_neo4j_insert()
                == resources[i].serialize_for_neo4j_insert()
            )

    # del_query = proj.delete()
    # res_del_query = res.delete()
    # with twig4j_orm.conn.session() as sess:
    #     res_del_query.execute(sess, {"id": rsrc_id})
    #     del_query.execute(sess, {"id": proj_id})
