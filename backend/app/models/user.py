from sqlalchemy import Column, DateTime, Enum, Integer, String, text
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    employee_id = Column(
        Integer,
        unique=True,
        nullable=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        nullable=False,
        unique=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        Enum("employee", "admin"),
        nullable=True,
        server_default="employee"
    )

    created_date = Column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

    leaves = relationship(
        "Leave",
        back_populates="user"
    )