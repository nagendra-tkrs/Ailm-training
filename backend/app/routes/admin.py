from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import require_role
from app.services import user_service


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)


@router.get("/dashboard")
def admin_dashboard(
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    return user_service.get_admin_dashboard(db=db)
