from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.types import DateTime

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column('id', Integer, primary_key=True)
    username = Column('username', String, unique=True)
    email = Column('email', String, unique=True)
    kratos_user_id = Column('kratos_user_id', String, unique=True)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    date_created = Column('date_created', DateTime)
    date_last_login = Column('date_last_login', DateTime)
