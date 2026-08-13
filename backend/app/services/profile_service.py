from sqlalchemy.orm import Session

from app.models.user import User
from app.models.employee_profile import EmployeeProfile
from app.core.security import hash_password, verify_password


def _error(detail: str, status_code: int):
    return {"detail": detail, "status_code": status_code}


def get_or_create_profile(
    db: Session,
    user: User
) -> EmployeeProfile:
    profile = (
        db.query(EmployeeProfile)
        .filter(EmployeeProfile.user_id == user.id)
        .first()
    )

    if profile is None:
        profile = EmployeeProfile(
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=user.role or "employee",
            address=None,
            phone_number=None,
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

    return profile


def serialize_profile(
    user: User,
    profile: EmployeeProfile
) -> dict:
    return {
        "employee_id": user.employee_id,
        "role": user.role or "employee",
        "name": profile.name,
        "email": profile.email,
        "address": profile.address,
        "phone_number": profile.phone_number,
    }


def get_profile(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        return None, _error("User not found", 404)

    profile = get_or_create_profile(db, user)

    return serialize_profile(user, profile), None


def update_profile(
    db: Session,
    user_id: int,
    name: str,
    email: str,
    address,
    phone_number
):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        return None, _error("User not found", 404)

    # Email must stay unique in the users table (used for login)
    email_taken = (
        db.query(User)
        .filter(User.email == email, User.id != user_id)
        .first()
    )

    if email_taken:
        return None, _error("Email is already in use by another account", 400)

    profile = get_or_create_profile(db, user)

    profile.name = name
    profile.email = email
    profile.address = address
    profile.phone_number = phone_number

    # Keep the users table in sync so login validation uses the new data
    user.name = name
    user.email = email

    db.commit()
    db.refresh(profile)

    return serialize_profile(user, profile), None


def reset_password(
    db: Session,
    user_id: int,
    current_password: str,
    new_password: str
):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        return _error("User not found", 404)

    if not verify_password(current_password, user.password):
        return _error("Current password is incorrect", 400)

    user.password = hash_password(new_password)
    db.commit()

    return None
