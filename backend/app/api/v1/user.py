from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.services import user as user_services
from app.schemas.user import User, UserCreate, UserLogin, UserUpdate, Token
from app.core import security

user_router = APIRouter()

@user_router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(deps.get_db)):
    db_user = await user_services.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Email Already Exists!!")
    
    db_user = await user_services.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Username Already Exists!!")

    return await user_services.create_user(db, user)
    
@user_router.put("/user_update/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    user: UserUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )
    try:
        db_user = await user_services.update_user(db, user=user, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found!!")
    return db_user


@user_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(credentials: UserLogin,db: AsyncSession = Depends(deps.get_db),) -> Token:
    user = await user_services.authenticate_user_by_email(
        db, email=credentials.email, password=credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    access_token = security.get_access_token(subject=user.id)
    return Token(access_token=access_token, token_type="bearer")

@user_router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )

    success = await user_services.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None
