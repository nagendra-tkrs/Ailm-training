from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.models.leave_balance import create_default_balances
from app.models.employee_profile import EmployeeProfile
from app.services.user_service import generate_employee_id


def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role: str
):
    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        return None

    # Hash password
    hashed_password = hash_password(password)

    # Create user; retry with a fresh random employee id if two concurrent
    # registrations happened to pick the same number.
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
        return None

    db.refresh(user)

    # Give the user a leave balance for every leave type
    if role == "employee":
        create_default_balances(db, user.id)

    # Create an empty profile so the employee can fill in contact details
    db.add(
        EmployeeProfile(
            user_id=user.id,
            name=name,
            email=email,
            role=role,
        )
    )
    db.commit()

    return user


def login_user(
    db: Session,
    email: str,
    password: str
):
    # Find user by email
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    # User does not exist
    if not user:
        return None

    # Verify password
    if not verify_password(password, user.password):
        return None

    return user
