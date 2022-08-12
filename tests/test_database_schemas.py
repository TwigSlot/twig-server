import os
from neomodel import db
from twig_server.database.User import User

db.set_connection(os.getenv("NEO4J_BOLT_URL"))


def test_user():
    jim = User(username='jim', email='tanchienhao@gmail.com')
    jim.save()
    print(jim.id)