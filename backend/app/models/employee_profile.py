from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, text

from app.database.database import Base


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False,
        server_default="employee"
    )

    address = Column(
        String(255),
        nullable=True
    )

    phone_number = Column(
        String(20),
        nullable=True
    )

    created_at = Column(
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
