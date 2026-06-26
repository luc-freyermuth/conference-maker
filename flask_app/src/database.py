from sqlalchemy import create_engine, Text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class UserSession(Base):
    __tablename__ = "session"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    data: Mapped[str] = mapped_column(Text)



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