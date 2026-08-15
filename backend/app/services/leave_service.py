from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.leave import Leave
from app.models.leave_balance import LeaveBalance
from app.models.user import User


# Mapping between the Day-3 API values (CASUAL / SICK / EARNED) and the
# display names stored in the database (Casual Leave / Sick Leave / Earned Leave).
LEAVE_TYPE_MAP = {
    "CASUAL": "Casual Leave",
    "SICK": "Sick Leave",
    "EARNED": "Earned Leave",
}

REVERSE_LEAVE_TYPE_MAP = {
    value: key
    for key, value in LEAVE_TYPE_MAP.items()
}

STATUS_MAP = {
    "pending": "PENDING",
    "approved": "APPROVED",
    "rejected": "REJECTED",
}


def calculate_leave_days(
    start_date: date,
    end_date: date
) -> int:
    """Inclusive day count: 2026-08-12 to 2026-08-14 == 3 days."""
    return (end_date - start_date).days + 1


def normalize_leave_type(leave_type: str) -> Optional[str]:
    return LEAVE_TYPE_MAP.get(leave_type.upper())


def _overlap_exists(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date,
    exclude_id: Optional[int] = None
) -> Optional[Leave]:
    query = (
        db.query(Leave)
        .filter(
            Leave.user_id == user_id,
            Leave.status.in_(["pending", "approved"]),
            Leave.start_date <= end_date,
            Leave.end_date >= start_date,
        )
    )

    if exclude_id is not None:
        query = query.filter(Leave.id != exclude_id)

    return query.first()


def serialize_leave(leave: Leave) -> dict:
    return {
        "id": leave.id,
        "leaveType": leave.leave_type,
        "startDate": leave.start_date.isoformat(),
        "endDate": leave.end_date.isoformat(),
        "days": leave.days,
        "reason": leave.reason,
        "status": leave.status,
        "createdDate": leave.created_date.isoformat()
        if leave.created_date
        else None,
    }


def get_balance_row(
    db: Session,
    user_id: int,
    leave_type: str
) -> Optional[LeaveBalance]:
    return (
        db.query(LeaveBalance)
        .filter(
            LeaveBalance.user_id == user_id,
            LeaveBalance.leave_type == leave_type,
        )
        .first()
    )


def apply_leave(
    db: Session,
    user_id: int,
    leave_type: str,
    start_date: date,
    end_date: date,
    days: int,
    reason: str
):
    # Date order check
    if start_date > end_date:
        return None, "Start date cannot be after end date"

    # Backend always recalculates the duration, never trusts the frontend
    days = calculate_leave_days(start_date, end_date)

    # Overlapping request check
    overlap = _overlap_exists(db, user_id, start_date, end_date)

    if overlap:
        return None, "You already have a leave request overlapping these dates"

    # Leave balance check
    balance = get_balance_row(db, user_id, leave_type)

    if balance is None:
        return None, f"Leave balance not configured for '{leave_type}'"

    remaining = balance.remaining_days

    if days > remaining:
        return (
            None,
            f"Insufficient balance. You have {remaining} day(s) "
            f"left for '{leave_type}' but requested {days} day(s).",
        )

    leave = Leave(
        user_id=user_id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        days=days,
        reason=reason,
        status="pending",
        employee_id=db.query(User.employee_id)
        .filter(User.id == user_id)
        .scalar(),
    )

    db.add(leave)
    db.commit()
    db.refresh(leave)

    return leave, None


def get_dashboard_data(db: Session, user_id: int) -> dict:
    balances = (
        db.query(LeaveBalance)
        .filter(LeaveBalance.user_id == user_id)
        .all()
    )

    balance_map = {
        balance.leave_type: balance.remaining_days
        for balance in balances
    }

    leave_balance = {
        "casual": balance_map.get("Casual Leave", 0),
        "sick": balance_map.get("Sick Leave", 0),
        "earned": balance_map.get("Earned Leave", 0),
    }

    # Query only the specific columns we need to avoid DB errors when the
    # optional `employee_id` column is missing in development databases.
    pending_rows = (
        db.query(
            Leave.id,
            Leave.leave_type,
            Leave.start_date,
            Leave.end_date,
            Leave.days,
            Leave.reason,
            Leave.status,
            Leave.created_date,
        )
        .filter(Leave.user_id == user_id, Leave.status == "pending")
        .order_by(Leave.id.desc())
        .all()
    )

    approved_rows = (
        db.query(
            Leave.id,
            Leave.leave_type,
            Leave.start_date,
            Leave.end_date,
            Leave.days,
            Leave.reason,
            Leave.status,
            Leave.created_date,
        )
        .filter(Leave.user_id == user_id, Leave.status == "approved")
        .order_by(Leave.id.desc())
        .all()
    )

    def row_to_dict(row):
        return {
            "id": row[0],
            "leaveType": row[1],
            "startDate": row[2].isoformat() if row[2] else None,
            "endDate": row[3].isoformat() if row[3] else None,
            "days": row[4],
            "reason": row[5],
            "status": row[6],
            "createdDate": row[7].isoformat() if row[7] else None,
        }

    return {
        "leaveBalance": leave_balance,
        "pendingLeaves": [row_to_dict(r) for r in pending_rows],
        "approvedLeaves": [row_to_dict(r) for r in approved_rows],
    }


def get_my_leaves(db: Session, user_id: int) -> list:
    leaves = (
        db.query(Leave)
        .filter(Leave.user_id == user_id)
        .order_by(Leave.id.desc())
        .all()
    )

    return [serialize_leave(leave) for leave in leaves]


def get_all_leaves(
    db: Session,
    status_filter: Optional[str] = None
) -> list:
    query = db.query(Leave)

    if status_filter and status_filter in ("pending", "approved", "rejected"):
        query = query.filter(Leave.status == status_filter)

    leaves = query.order_by(Leave.id.desc()).all()

    result = []
    users = {
        user.id: user
        for user in db.query(User).all()
    }

    for leave in leaves:
        item = serialize_leave(leave)
        user = users.get(leave.user_id)

        item["employee"] = {
            "id": leave.user_id,
            "name": user.name if user else None,
            "email": user.email if user else None,
        }

        result.append(item)

    return result


def decide_leave(
    db: Session,
    leave_id: int,
    decision: str
):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()

    if leave is None:
        return None, "Leave request not found"

    if leave.status != "pending":
        return None, f"This request was already {leave.status}"

    if decision == "approved":
        balance = get_balance_row(db, leave.user_id, leave.leave_type)

        if balance is not None:
            balance.used_days += leave.days
            db.add(balance)

    leave.status = decision
    db.commit()
    db.refresh(leave)

    return leave, None


def delete_leave(db: Session, leave_id: int, user_id: int):
    leave = (
        db.query(Leave)
        .filter(Leave.id == leave_id, Leave.user_id == user_id)
        .first()
    )

    if leave is None:
        return "Leave request not found"

    if leave.status != "pending":
        return "Only pending requests can be deleted"

    db.delete(leave)
    db.commit()

    return None


# --------------------------------------------------------------------------
# Day-3 spec: /api/leaves CRUD (snake_case contract)
# --------------------------------------------------------------------------


def serialize_leave_spec(leave: Leave) -> dict:
    employee_id = leave.employee_id

    if employee_id is None and leave.user is not None:
        employee_id = leave.user.employee_id

    return {
        "id": leave.id,
        "employee_id": employee_id,
        "leave_type": REVERSE_LEAVE_TYPE_MAP.get(
            leave.leave_type,
            leave.leave_type
        ),
        "start_date": leave.start_date.isoformat(),
        "end_date": leave.end_date.isoformat(),
        "leave_days": leave.days,
        "reason": leave.reason,
        "status": STATUS_MAP.get(leave.status, leave.status),
        "created_at": leave.created_date.isoformat()
        if leave.created_date
        else None,
        "updated_at": leave.updated_at.isoformat()
        if leave.updated_at
        else None,
    }


def _leave_error(detail: str, status_code: int):
    return {"detail": detail, "status_code": status_code}


def create_leave(
    db: Session,
    user_id: int,
    leave_type: str,
    start_date: date,
    end_date: date,
    reason: str
):
    normalized = normalize_leave_type(leave_type)

    if normalized is None:
        return (
            None,
            _leave_error("Invalid leave type", 400),
        )

    if start_date > end_date:
        return (
            None,
            _leave_error("End date cannot be earlier than start date", 400),
        )

    leave_days = calculate_leave_days(start_date, end_date)

    if _overlap_exists(db, user_id, start_date, end_date):
        return (
            None,
            _leave_error(
                "Leave request overlaps with an existing leave",
                400,
            ),
        )

    balance = get_balance_row(db, user_id, normalized)

    if balance is None:
        return (
            None,
            _leave_error(
                "Leave balance not configured for this leave type",
                400,
            ),
        )

    if leave_days > balance.remaining_days:
        return (
            None,
            _leave_error(
                f"Insufficient leave balance. Available: "
                f"{balance.remaining_days} day(s), requested: "
                f"{leave_days} day(s).",
                400,
            ),
        )

    leave = Leave(
        user_id=user_id,
        leave_type=normalized,
        start_date=start_date,
        end_date=end_date,
        days=leave_days,
        reason=reason,
        status="pending",
        employee_id=db.query(User.employee_id)
        .filter(User.id == user_id)
        .scalar(),
    )

    db.add(leave)
    db.commit()
    db.refresh(leave)

    return leave, None


def list_employee_leaves(db: Session, user_id: int) -> list:
    return (
        db.query(Leave)
        .filter(Leave.user_id == user_id)
        .order_by(Leave.id.desc())
        .all()
    )


def update_leave(
    db: Session,
    user_id: int,
    leave_id: int,
    leave_type: str,
    start_date: date,
    end_date: date,
    reason: str
):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()

    if leave is None:
        return (
            None,
            _leave_error("Leave request not found", 404),
        )

    if leave.user_id != user_id:
        return (
            None,
            _leave_error(
                "You cannot modify another employee's leave request",
                403,
            ),
        )

    if leave.status != "pending":
        return (
            None,
            _leave_error(
                "Only pending leave requests can be updated",
                400,
            ),
        )

    normalized = normalize_leave_type(leave_type)

    if normalized is None:
        return (
            None,
            _leave_error("Invalid leave type", 400),
        )

    if start_date > end_date:
        return (
            None,
            _leave_error("End date cannot be earlier than start date", 400),
        )

    leave_days = calculate_leave_days(start_date, end_date)

    if _overlap_exists(
        db,
        user_id,
        start_date,
        end_date,
        exclude_id=leave.id,
    ):
        return (
            None,
            _leave_error(
                "Leave request overlaps with an existing leave",
                400,
            ),
        )

    balance = get_balance_row(db, user_id, normalized)

    if balance is None:
        return (
            None,
            _leave_error(
                "Leave balance not configured for this leave type",
                400,
            ),
        )

    if leave_days > balance.remaining_days:
        return (
            None,
            _leave_error(
                f"Insufficient leave balance. Available: "
                f"{balance.remaining_days} day(s), requested: "
                f"{leave_days} day(s).",
                400,
            ),
        )

    leave.leave_type = normalized
    leave.start_date = start_date
    leave.end_date = end_date
    leave.days = leave_days
    leave.reason = reason

    db.commit()
    db.refresh(leave)

    return leave, None


def delete_employee_leave(
    db: Session,
    user_id: int,
    leave_id: int
):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()

    if leave is None:
        return _leave_error("Leave request not found", 404)

    if leave.user_id != user_id:
        return _leave_error(
            "You cannot delete another employee's leave request",
            403,
        )

    if leave.status != "pending":
        return _leave_error(
            "Only pending leave requests can be deleted",
            400,
        )

    db.delete(leave)
    db.commit()

    return None


# --------------------------------------------------------------------------
# Admin leave management: /api/admin/leaves
# --------------------------------------------------------------------------


def get_admin_leave_list(
    db: Session,
    status_filter: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    limit: int = 10,
):
    if status_filter and status_filter not in ("pending", "approved", "rejected"):
        return None, _leave_error(
            "Invalid status filter. Use pending, approved or rejected",
            400,
        )

    query = db.query(Leave)

    if status_filter:
        query = query.filter(Leave.status == status_filter)

    if start_date is not None:
        query = query.filter(Leave.start_date >= start_date)

    if end_date is not None:
        query = query.filter(Leave.end_date <= end_date)

    total_records = query.count()

    leaves = (
        query.order_by(Leave.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    users = {
        user.id: user
        for user in db.query(User).all()
    }

    items = []
    for leave in leaves:
        item = serialize_leave(leave)
        user = users.get(leave.user_id)

        item["employee"] = {
            "id": leave.user_id,
            "name": user.name if user else None,
            "email": user.email if user else None,
        }

        items.append(item)

    pagination = {
        "current_page": page,
        "page_size": limit,
        "total_records": total_records,
        "total_pages": (total_records + limit - 1) // limit if limit else 0,
    }

    return {"leaves": items, "pagination": pagination}, None


def approve_leave(
    db: Session,
    leave_id: int
):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()

    if leave is None:
        return None, _leave_error("Leave request not found", 404)

    if leave.status != "pending":
        return None, _leave_error(
            f"Only pending leave requests can be approved "
            f"(current status: {leave.status})",
            400,
        )

    balance = get_balance_row(db, leave.user_id, leave.leave_type)

    if balance is not None:
        balance.used_days += leave.days
        db.add(balance)

    leave.status = "approved"
    db.commit()
    db.refresh(leave)

    return leave, None


def reject_leave(
    db: Session,
    leave_id: int
):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()

    if leave is None:
        return None, _leave_error("Leave request not found", 404)

    if leave.status != "pending":
        return None, _leave_error(
            f"Only pending leave requests can be rejected "
            f"(current status: {leave.status})",
            400,
        )

    leave.status = "rejected"
    db.commit()
    db.refresh(leave)

    return leave, None
