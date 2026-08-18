import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import require_admin
from app.services import user_service

logger = logging.getLogger("app.routes.admin")

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)


@router.get("/dashboard")
def admin_dashboard(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        return user_service.get_admin_dashboard(db=db)
    except SQLAlchemyError:
        logger.error("Database error fetching admin dashboard", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load admin dashboard"
        )
