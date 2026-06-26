from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables.base import Base
from tables.user_session import UserSession


class Database:
    def __init__(self):
        self.engine = create_engine(
            "sqlite:///cache.db", connect_args={"autocommit": True}
        )
        self.Session = sessionmaker(self.engine)

        self.init_tables()

    def init_tables(self):
        Base.metadata.create_all(self.engine)

    
db = Database()