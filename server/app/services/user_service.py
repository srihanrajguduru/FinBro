
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password
from app.models.schemas import OnboardingRequest, RegisterRequest
from app.models.user import User, UserType

SAVINGS_TARGET_PROFESSIONAL = 0.20
SAVINGS_TARGET_STUDENT = 0.15


def get_savings_target_rate(user_type: UserType) -> float:
    return SAVINGS_TARGET_PROFESSIONAL if user_type == UserType.PROFESSIONAL else SAVINGS_TARGET_STUDENT


async def create_user(db: AsyncSession, data: RegisterRequest) -> User:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    await db.flush()
    return user


async def complete_onboarding(db: AsyncSession, user: User, data: OnboardingRequest) -> User:
    user.user_type = data.user_type
    user.monthly_salary = data.monthly_salary
    if data.user_type == UserType.STUDENT:
        user.monthly_spending_limit = data.monthly_spending_limit or data.monthly_salary * 0.7
    else:
        user.monthly_spending_limit = None
    user.onboarding_complete = True
    await db.flush()
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
