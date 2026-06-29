from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password
from app.core.config import settings
from app.models.user import (
    Debt,
    Goal,
    GoalStatus,
    Transaction,
    TransactionCategory,
    TransactionType,
    User,
    UserType,
)


async def seed_demo_data(db: AsyncSession) -> User:
    user = User(
        id=settings.DEMO_USER_ID,
        email="demo@finbro.app",
        hashed_password=hash_password("demo1234"),
        full_name="Demo User",
        user_type=UserType.PROFESSIONAL,
        monthly_salary=5000.0,
        onboarding_complete=True,
        fbt_balance=150.0,
    )
    db.add(user)
    await db.flush()

    now = datetime.now(UTC)
    transactions = [
        Transaction(
            user_id=user.id, amount=5000, transaction_type=TransactionType.INCOME,
            category=TransactionCategory.INCOME, description="Salary", date=now,
        ),
        Transaction(
            user_id=user.id, amount=450, transaction_type=TransactionType.EXPENSE,
            category=TransactionCategory.FOOD, description="Groceries", date=now - timedelta(days=2),
        ),
        Transaction(
            user_id=user.id, amount=120, transaction_type=TransactionType.EXPENSE,
            category=TransactionCategory.TRANSPORT, description="Gas", date=now - timedelta(days=5),
        ),
        Transaction(
            user_id=user.id, amount=200, transaction_type=TransactionType.EXPENSE,
            category=TransactionCategory.ENTERTAINMENT, description="Streaming", date=now - timedelta(days=1),
        ),
    ]
    for tx in transactions:
        db.add(tx)

    goals = [
        Goal(
            user_id=user.id, name="Emergency Fund", target_amount=10000,
            current_amount=3500, monthly_target=541.67, status=GoalStatus.ACTIVE,
        ),
        Goal(
            user_id=user.id, name="Vacation", target_amount=3000,
            current_amount=1200, monthly_target=150, status=GoalStatus.ACTIVE,
        ),
    ]
    for g in goals:
        db.add(g)

    debts = [
        Debt(user_id=user.id, name="Credit Card", balance=2500, interest_rate=18.99, minimum_payment=75),
        Debt(user_id=user.id, name="Student Loan", balance=15000, interest_rate=5.5, minimum_payment=200),
    ]
    for d in debts:
        db.add(d)

    await db.flush()
    return user
