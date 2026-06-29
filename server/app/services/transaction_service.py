from datetime import UTC, datetime

from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import TransactionCreate, TransactionSummary, TransactionUpdate
from app.models.user import (
    Notification,
    NotificationType,
    Transaction,
    TransactionType,
    User,
    UserType,
)
from app.services.user_service import get_savings_target_rate


async def create_transaction(db: AsyncSession, user: User, data: TransactionCreate) -> Transaction:
    if user.user_type == UserType.STUDENT and data.transaction_type == TransactionType.EXPENSE:
        await _check_student_spending_limit(db, user, data.amount)

    tx = Transaction(
        user_id=user.id,
        amount=data.amount,
        transaction_type=data.transaction_type,
        category=data.category,
        description=data.description,
        date=data.date or datetime.now(UTC),
    )
    db.add(tx)
    await db.flush()
    return tx


async def _check_student_spending_limit(db: AsyncSession, user: User, new_amount: float) -> None:
    if user.monthly_spending_limit is None:
        return

    now = datetime.now(UTC)
    result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            and_(
                Transaction.user_id == user.id,
                Transaction.transaction_type == TransactionType.EXPENSE,
                extract("month", Transaction.date) == now.month,
                extract("year", Transaction.date) == now.year,
            )
        )
    )
    current_spent = float(result.scalar() or 0)
    total = current_spent + new_amount
    limit = user.monthly_spending_limit

    pct = (total / limit) * 100 if limit > 0 else 0

    if total > limit:
        raise ValueError(f"Spending limit exceeded. Limit: ${limit:.2f}, would spend: ${total:.2f}")

    if pct >= 95:
        await _create_warning_notification(
            db, user, "Critical spending alert",
            f"You've used {pct:.0f}% of your monthly limit (${total:.2f}/${limit:.2f}).",
            NotificationType.SPENDING_WARNING,
        )
    elif pct >= 80:
        await _create_warning_notification(
            db, user, "Spending warning",
            f"You've used {pct:.0f}% of your monthly limit (${total:.2f}/${limit:.2f}).",
            NotificationType.SPENDING_WARNING,
        )


async def _create_warning_notification(
    db: AsyncSession, user: User, title: str, message: str, ntype: NotificationType
) -> None:
    notif = Notification(user_id=user.id, title=title, message=message, notification_type=ntype)
    db.add(notif)


async def get_transactions(db: AsyncSession, user_id: str) -> list[Transaction]:
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.date.desc())
    )
    return list(result.scalars().all())


async def get_transaction(db: AsyncSession, user_id: str, tx_id: str) -> Transaction | None:
    result = await db.execute(
        select(Transaction).where(and_(Transaction.id == tx_id, Transaction.user_id == user_id))
    )
    return result.scalar_one_or_none()


async def update_transaction(
    db: AsyncSession, user: User, tx: Transaction, data: TransactionUpdate
) -> Transaction:
    if data.amount is not None:
        tx.amount = data.amount
    if data.transaction_type is not None:
        tx.transaction_type = data.transaction_type
    if data.category is not None:
        tx.category = data.category
    if data.description is not None:
        tx.description = data.description
    if data.date is not None:
        tx.date = data.date
    await db.flush()
    return tx


async def delete_transaction(db: AsyncSession, tx: Transaction) -> None:
    await db.delete(tx)
    await db.flush()


async def get_summary(db: AsyncSession, user: User) -> TransactionSummary:
    now = datetime.now(UTC)
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.user_id == user.id,
                extract("month", Transaction.date) == now.month,
                extract("year", Transaction.date) == now.year,
            )
        )
    )
    txs = list(result.scalars().all())

    total_income = sum(t.amount for t in txs if t.transaction_type == TransactionType.INCOME)
    total_expenses = sum(t.amount for t in txs if t.transaction_type == TransactionType.EXPENSE)
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
    target_rate = get_savings_target_rate(user.user_type)
    savings_target = user.monthly_salary * target_rate

    by_category: dict[str, float] = {}
    for t in txs:
        if t.transaction_type == TransactionType.EXPENSE:
            cat = t.category.value
            by_category[cat] = by_category.get(cat, 0) + t.amount

    return TransactionSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_savings=net_savings,
        savings_rate=savings_rate,
        savings_target=savings_target,
        by_category=by_category,
    )
