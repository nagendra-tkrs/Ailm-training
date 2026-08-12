from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User


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

    # Create user
    user = User(
        name=name,
        email=email,
        password=hashed_password,
        role=role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

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