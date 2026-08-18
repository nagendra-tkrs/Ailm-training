from datetime import datetime, timedelta, timezone
import uuid

from jose import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings


# Password hashing
pwd_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return pwd_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    try:
        return pwd_hasher.verify(
            hashed_password,
            plain_password
        )
    except VerifyMismatchError:
        return False


# JWT token generation
def create_access_token(
    user_id: int,
    email: str,
    role: str
) -> str:

    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token