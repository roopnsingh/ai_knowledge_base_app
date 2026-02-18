from typing import AsyncGenerator
from uuid import UUID
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings
from app.database.session import SessionLocal
from app.services import user as user_services
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/user/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        token_type = payload.get("type")
        sub = payload.get("sub")
        iss = payload.get("iss")
        if token_type != "access" or sub is None or iss != settings.PROJECT_NAME:
            raise credentials_exception
        user_id = UUID(sub)
    except (JWTError, ValidationError, ValueError):
        raise credentials_exception

    user = await user_services.get_user(db, user_id=user_id)

    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user






        
