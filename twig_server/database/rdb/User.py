from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    # Note: This is postgres specific. Let's assume we won't migrate from
    # postgres anyway.
    kratos_user_id = Column('kratos_user_id', String, unique=True)

    # TODO: A list of projects that the user has access to needs to be stored
    #  Likely in a separate table, with a foreign key to this table


class ProjectPermissions(Base):
    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', String, ForeignKey('user.kratos_user_id'))
    project_id = Column('project_id', Integer)
    # TODO: This should NOT be a string. It should be an enum
    # TODO: Investigate finer grained permissions system?
    role = Column('role', String)
