import logging
import random

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.leave_balance import LeaveBalance
from app.models.leave import Leave

logger = logging.getLogger("app.user_service")

EMPLOYEE_ID_MIN = 1000
EMPLOYEE_ID_MAX = 9999
MAX_ID_RETRIES = 100


def generate_employee_id(db: Session) -> int:
    used = set(
        row[0]
        for row in db.query(User.employee_id)
        .filter(User.employee_id.isnot(None))
        .all()
    )

    for _ in range(MAX_ID_RETRIES):
        candidate = random.randint(EMPLOYEE_ID_MIN, EMPLOYEE_ID_MAX)

        if candidate not in used:
            return candidate

    logger.error("Could not generate unique employee ID after %d retries", MAX_ID_RETRIES)
    raise RuntimeError("Could not generate unique employee ID")


def list_users(db: Session) -> list:
    return (
        db.query(User)
        .order_by(User.id.asc())
        .all()
    )


def get_user_with_balances(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        return None

    balances = (
        db.query(LeaveBalance)
        .filter(LeaveBalance.user_id == user_id)
        .all()
    )

    return {
        "id": user.id,
        "employee_id": user.employee_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "createdDate": (
            user.created_date.isoformat()
            if user.created_date
            else None
        ),
        "leaveBalance": {
            balance.leave_type: {
                "total": balance.total_days,
                "used": balance.used_days,
                "remaining": balance.remaining_days,
            }
            for balance in balances
        },
    }


def get_admin_dashboard(db: Session) -> dict:
    total_employees = (
        db.query(User)
        .filter(User.role == "employee")
        .count()
    )

    total_admins = (
        db.query(User)
        .filter(User.role == "admin")
        .count()
    )

    pending_count = (
        db.query(Leave)
        .filter(Leave.status == "pending")
        .count()
    )

    approved_count = (
        db.query(Leave)
        .filter(Leave.status == "approved")
        .count()
    )

    rejected_count = (
        db.query(Leave)
        .filter(Leave.status == "rejected")
        .count()
    )

    recent = (
        db.query(Leave)
        .order_by(Leave.id.desc())
        .limit(8)
        .all()
    )

    users = {
        user.id: user
        for user in db.query(User).all()
    }

    recent_leaves = []
    for leave in recent:
        item = {
            "id": leave.id,
            "leaveType": leave.leave_type,
            "startDate": leave.start_date.isoformat(),
            "endDate": leave.end_date.isoformat(),
            "days": leave.days,
            "status": leave.status,
        }
        user = users.get(leave.user_id)

        item["employeeName"] = user.name if user else None
        recent_leaves.append(item)

    return {
        "stats": {
            "totalEmployees": total_employees,
            "totalAdmins": total_admins,
            "pending": pending_count,
            "approved": approved_count,
            "rejected": rejected_count,
        },
        "recentLeaves": recent_leaves,
    }
