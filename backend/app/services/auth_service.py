import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.models.leave_balance import create_default_balances
from app.models.employee_profile import EmployeeProfile
from app.services.user_service import generate_employee_id

logger = logging.getLogger("app.auth_service")


def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role: str
):
    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        return None

    hashed_password = hash_password(password)

    user = None

    for _ in range(10):
        user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role,
            employee_id=generate_employee_id(db),
        )

        db.add(user)

        try:
            db.commit()
            break
        except IntegrityError:
            db.rollback()
            user = None

    if user is None:
        logger.error("Failed to register user after 10 retries: %s", email)
        return None

    db.refresh(user)

    try:
        if role == "employee":
            create_default_balances(db, user.id)

        db.add(
            EmployeeProfile(
                user_id=user.id,
                name=name,
                email=email,
                role=role,
            )
        )
        db.commit()
    except Exception:
        logger.error(
            "Failed to create profile/balances for user %d", user.id,
            exc_info=True,
        )
        db.rollback()

    return user


def login_user(
    db: Session,
    email: str,
    password: str
):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user
