from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services.auth_service import register_user, login_user
from app.core.security import create_access_token
from fastapi import Depends

from app.core.dependencies import require_role


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    user = register_user(
        db=db,
        name=request.name,
        email=request.email,
        password=request.password,
        role=request.role
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    return {
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_date": user.created_date
        }
    }
@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = login_user(
        db=db,
        email=request.email,
        password=request.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/admin-test")
def admin_test(
    current_user: dict = Depends(require_role("admin"))
):
    return {
        "message": "Admin access granted",
        "user": current_user
    }