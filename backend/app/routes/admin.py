from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import require_role
from app.services import leave_service, user_service


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)


def _raise_error(error: dict):
    raise HTTPException(
        status_code=error["status_code"],
        detail=error["detail"],
    )


@router.get("/dashboard")
def admin_dashboard(
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    return user_service.get_admin_dashboard(db=db)


@router.get("/leaves")
def list_admin_leaves(
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    result, error = leave_service.get_admin_leave_list(
        db=db,
        status_filter=status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit,
    )

    if error:
        _raise_error(error)

    return result


@router.put("/leaves/{leave_id}/approve")
def approve_leave(
    leave_id: int,
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    leave, error = leave_service.approve_leave(
        db=db,
        leave_id=leave_id,
    )

    if error:
        _raise_error(error)

    return {
        "message": "Leave request approved successfully",
        "leave": leave_service.serialize_leave(leave),
    }


@router.put("/leaves/{leave_id}/reject")
def reject_leave(
    leave_id: int,
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    leave, error = leave_service.reject_leave(
        db=db,
        leave_id=leave_id,
    )

    if error:
        _raise_error(error)

    return {
        "message": "Leave request rejected successfully",
        "leave": leave_service.serialize_leave(leave),
    }
