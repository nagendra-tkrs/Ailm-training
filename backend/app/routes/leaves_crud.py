from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.leave_crud import (
    CreateLeaveRequest,
    UpdateLeaveRequest,
)
from app.services import leave_service


router = APIRouter(
    prefix="/api/leaves",
    tags=["Leaves CRUD"]
)


def _raise_error(error: dict):
    raise HTTPException(
        status_code=error["status_code"],
        detail=error["detail"],
    )


@router.post("")
def create_leave(
    request: CreateLeaveRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    leave, error = leave_service.create_leave(
        db=db,
        user_id=current_user["user_id"],
        leave_type=request.leave_type,
        start_date=request.start_date,
        end_date=request.end_date,
        reason=request.reason,
    )

    if error:
        _raise_error(error)

    return leave_service.serialize_leave_spec(leave)


@router.get("")
def list_leaves(
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(8, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        result, error = leave_service.get_employee_leave_list(
            db=db,
            user_id=current_user["user_id"],
            status_filter=status,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit,
        )

        if error:
            _raise_error(error)

        return result
    except Exception as error:
        import traceback

        traceback.print_exc()

        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=str(error))


@router.put("/{leave_id}")
def update_leave(
    leave_id: int,
    request: UpdateLeaveRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    leave, error = leave_service.update_leave(
        db=db,
        user_id=current_user["user_id"],
        leave_id=leave_id,
        leave_type=request.leave_type,
        start_date=request.start_date,
        end_date=request.end_date,
        reason=request.reason,
    )

    if error:
        _raise_error(error)

    return leave_service.serialize_leave_spec(leave)


@router.delete("/{leave_id}")
def delete_leave(
    leave_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    error = leave_service.delete_employee_leave(
        db=db,
        user_id=current_user["user_id"],
        leave_id=leave_id,
    )

    if error:
        _raise_error(error)

    return {"message": "Leave request deleted successfully"}
