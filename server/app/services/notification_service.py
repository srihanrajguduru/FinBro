import re

import httpx
from sqlalchemy import and_, extract, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ExpenseCreate,
    SpendingLimitStatus,
    TransactionCreate,
)
from app.models.user import Notification, Transaction, TransactionType, User, UserType
from app.services.transaction_service import create_transaction


async def get_notifications(db: AsyncSession, user_id: str) -> list[Notification]:
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
    )
    return list(result.scalars().all())


async def mark_read(db: AsyncSession, user_id: str, notif_id: str) -> Notification | None:
    result = await db.execute(
        select(Notification).where(Notification.id == notif_id, Notification.user_id == user_id)
    )
    notif = result.scalar_one_or_none()
    if notif:
        notif.read = True
        await db.flush()
    return notif


async def mark_all_read(db: AsyncSession, user_id: str) -> int:
    result = await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.read.is_(False))
        .values(read=True)
    )
    await db.flush()
    return result.rowcount


async def get_spending_limit_status(db: AsyncSession, user: User) -> SpendingLimitStatus:
    if user.user_type != UserType.STUDENT or user.monthly_spending_limit is None:
        return SpendingLimitStatus(
            limit=0, spent=0, remaining=0, percentage=0, warning_level="green"
        )

    from datetime import UTC, datetime

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
    spent = float(result.scalar() or 0)
    limit = user.monthly_spending_limit
    remaining = max(limit - spent, 0)
    pct = (spent / limit * 100) if limit > 0 else 0

    if spent >= limit:
        level = "blocked"
    elif pct >= 95:
        level = "red"
    elif pct >= 80:
        level = "yellow"
    else:
        level = "green"

    return SpendingLimitStatus(
        limit=limit, spent=spent, remaining=remaining, percentage=round(pct, 1), warning_level=level
    )


async def create_expense(db: AsyncSession, user: User, data: ExpenseCreate) -> Transaction:
    tx_data = TransactionCreate(
        amount=data.amount,
        transaction_type=TransactionType.EXPENSE,
        category=data.category,
        description=data.description,
        date=data.date,
    )
    return await create_transaction(db, user, tx_data)


INTENT_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "savings_rate",
        re.compile(r"saving|save|savings rate", re.I),
        "Your savings target is {target}% of your monthly salary. "
        "Track income vs expenses on the dashboard to monitor your rate.",
    ),
    (
        "debt_advice",
        re.compile(r"debt|pay off|loan|credit", re.I),
        "Try the Avalanche method (highest interest first) to save on interest, "
        "or Snowball (smallest balance first) for quick wins. Check the Debt page for simulations.",
    ),
    (
        "goal_help",
        re.compile(r"goal|target|save for", re.I),
        "Set SMART goals with deadlines on the Goals page. "
        "FinBro calculates your monthly target automatically. Complete a goal to earn 100 FBT tokens!",
    ),
    (
        "budget_help",
        re.compile(r"budget|spending|expense|limit", re.I),
        "Students have a monthly spending limit enforced server-side. "
        "You'll get warnings at 80% and 95% of your limit.",
    ),
    (
        "rewards_info",
        re.compile(r"reward|token|fbt|coin", re.I),
        "Earn FBT tokens: 100 for completing goals, 50 for monthly savings targets, "
        "75 for debt milestones. View your balance on the Rewards page.",
    ),
    (
        "retirement",
        re.compile(r"retire|retirement|401k|pension", re.I),
        "Use the Predictions feature for compound interest retirement projections. "
        "Start early — even small monthly contributions grow significantly over time.",
    ),
]


async def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Processes chat requests using the Gemini generative API if configured,
    otherwise falls back to rule-based intent pattern matching.
    """
    msg = request.message.strip()
    if not msg:
        return ChatResponse(reply="Ask me about savings, debt, goals, budgets, rewards, or retirement!", intent="empty")

    if settings.GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
            system_instruction = (
                "You are FinBro AI, a gamified personal finance assistant. "
                "Help the user save smarter, crush debt, and earn FBT rewards. "
                "Provide accurate, friendly, and concise financial advice. "
                "The platform features savings goals (completing goal mints 100 FBT), "
                "debt simulation (Avalanche and Snowball payoff strategies), "
                "and retirement forecasting using compound interest. "
                "Keep responses under 3-4 sentences whenever possible."
            )
            payload = {
                "contents": [{"parts": [{"text": msg}]}],
                "systemInstruction": {"parts": [{"text": system_instruction}]}
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, timeout=10.0)

            if res.status_code == 200:
                data = res.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                return ChatResponse(reply=reply, intent="gemini")
            else:
                print(f"Gemini API returned error status: {res.status_code}, response: {res.text}")
        except Exception as e:
            print(f"Error calling Gemini API: {e}")

    for intent, pattern, template in INTENT_PATTERNS:
        if pattern.search(msg):
            target = "20" if "professional" in msg.lower() else "15"
            reply = template.format(target=target)
            return ChatResponse(reply=reply, intent=intent)

    return ChatResponse(
        reply="I can help with savings, debt payoff, goals, budgeting, rewards, and retirement planning. "
        "Try asking about one of these topics!",
        intent="general",
    )
