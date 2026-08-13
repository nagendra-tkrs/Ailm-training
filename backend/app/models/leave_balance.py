from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from app.database.database import Base


class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "leave_type",
            name="uq_user_leave_type"
        ),
    )

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

    total_days = Column(
        Integer,
        nullable=False,
        default=0
    )

    used_days = Column(
        Integer,
        nullable=False,
        default=0
    )

    @property
    def remaining_days(self) -> int:
        return self.total_days - self.used_days


# Leave types and their default yearly allowance
LEAVE_TYPE_DEFAULTS = {
    "Casual Leave": 12,
    "Sick Leave": 10,
    "Earned Leave": 20,
}


def create_default_balances(db, user_id: int):
    """Give a new user the default leave balance for every leave type."""
    for leave_type, total_days in LEAVE_TYPE_DEFAULTS.items():
        db.add(
            LeaveBalance(
                user_id=user_id,
                leave_type=leave_type,
                total_days=total_days,
                used_days=0,
            )
        )
    db.commit()
