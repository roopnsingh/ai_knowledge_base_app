from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(**user.model_dump(exclude={"password"}))
    db_user.hashed_password = hashed_password
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


async def update_user(db: AsyncSession, user: UserUpdate, user_id: UUID) -> Optional[User]:
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    update_data = user.model_dump(exclude_unset=True)

    # Enforce email/username uniqueness if they are being changed
    if "email" in update_data:
        existing = await get_user_by_email(db, update_data["email"])
        if existing and existing.id != user_id:
            raise ValueError("Email already exists")
    if "username" in update_data:
        existing = await get_user_by_username(db, update_data["username"])
        if existing and existing.id != user_id:
            raise ValueError("Username already exists")

    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]

    for field, value in update_data.items():
        setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    """Soft delete: mark user as inactive instead of removing from DB."""
    db_user = await get_user(db, user_id)
    if not db_user:
        return False

    if not db_user.is_active:
        # Already inactive, treat as success
        return True

    db_user.is_active = False
    await db.commit()
    await db.refresh(db_user)

    return True


async def hard_delete_user(db: AsyncSession, user_id: UUID) -> bool:
    """Hard delete: permanently remove the user from DB."""
    db_user = await get_user(db, user_id)
    if not db_user:
        return False

    await db.delete(db_user)
    await db.commit()

    return True


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def authenticate_user_by_email(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

