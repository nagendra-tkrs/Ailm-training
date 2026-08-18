import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import require_employee
from app.services import leave_service

logger = logging.getLogger("app.routes.dashboard")

router = APIRouter(
    prefix="/api/employee",
    tags=["Employee Dashboard"]
)


@router.get("/dashboard")
def employee_dashboard(
    current_user: dict = Depends(require_employee),
    db: Session = Depends(get_db)
):
    try:
        data = leave_service.get_dashboard_data(
            db=db,
            user_id=current_user["user_id"],
        )

        return data
    except SQLAlchemyError:
        logger.error("Database error fetching dashboard", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard data"
        )
