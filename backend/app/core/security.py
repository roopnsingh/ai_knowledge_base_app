from datetime import timedelta, datetime, timezone
from argon2.exceptions import VerificationError, VerifyMismatchError
from jose import jwt, JWTError
from typing import Optional
from argon2 import PasswordHasher

from app.core.config import settings

def get_access_token(subject: str | int, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else: 
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        now = datetime.now(timezone.utc)
    payload = {
        "iat": now,
        "exp": expire,
        "sub": str(subject),
        "type": "access"
    }

    return jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)

ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
def get_password_hash(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, password)
    except (VerificationError, VerifyMismatchError):
        return False
