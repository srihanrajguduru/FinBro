from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    CurrentUser,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.core.config import settings
from app.core.database import get_db
from app.models.schemas import (
    LoginRequest,
    OnboardingRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.models.user import User
from app.services.demo_service import seed_demo_data
from app.services.user_service import complete_onboarding, create_user, get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await create_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    user.refresh_token = refresh
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    user.refresh_token = refresh
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(data.refresh_token, expected_type="refresh")
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or user.refresh_token != data.refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)
    user.refresh_token = new_refresh
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.post("/demo", response_model=TokenResponse)
async def demo_login(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == settings.DEMO_USER_ID))
    user = result.scalar_one_or_none()
    if not user:
        user = await seed_demo_data(db)

    return TokenResponse(
        access_token=settings.DEMO_TOKEN,
        refresh_token=settings.DEMO_TOKEN,
    )


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser):
    return user


@router.post("/onboarding", response_model=UserResponse)
async def onboarding(data: OnboardingRequest, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    user = await complete_onboarding(db, user, data)
    return user
