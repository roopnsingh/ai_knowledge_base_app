from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from typing import Optional

from core.config import settings

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
