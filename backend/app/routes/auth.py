from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services.auth_service import register_user, login_user
from app.core.security import create_access_token
from app.core.dependencies import get_current_user


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
        role="employee"
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
            "employee_id": user.employee_id,
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
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }
    }


@router.get("/me")
def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "Authentication successful",
        "user": current_user
    }
