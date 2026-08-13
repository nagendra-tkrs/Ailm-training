from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Leave(Base):
    __tablename__ = "leaves"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    leave_type = Column(
        String(50),
        nullable=False
    )

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
        nullable=False
    )

    days = Column(
        Integer,
        nullable=False
    )

    reason = Column(
        Text,
        nullable=False
    )

    status = Column(
        Enum("pending", "approved", "rejected"),
        nullable=False,
        server_default="pending"
    )

    created_date = Column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_at = Column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.now()
    )

    user = relationship(
        "User",
        back_populates="leaves"
    )
