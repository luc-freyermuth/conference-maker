from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column
from tables.base import Base

class UserSession(Base):
    __tablename__ = "session"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    data: Mapped[str] = mapped_column(Text)
