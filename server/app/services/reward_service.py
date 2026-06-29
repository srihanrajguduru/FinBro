import enum

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import RewardTransaction, RewardType, User


class RewardTypeEnum(str, enum.Enum):
    GOAL = "goal"
    MONTHLY_SAVINGS = "monthly_savings"
    DEBT_MILESTONE = "debt_milestone"


REWARD_AMOUNTS = {
    RewardTypeEnum.GOAL: 100,
    RewardTypeEnum.MONTHLY_SAVINGS: 50,
    RewardTypeEnum.DEBT_MILESTONE: 75,
}


async def mint_reward(
    db: AsyncSession,
    user: User,
    amount: float,
    reward_type: RewardTypeEnum,
    description: str,
) -> RewardTransaction:
    tx_hash = None
    if settings.use_mock_web3:
        tx_hash = f"mock-tx-{user.id[:8]}-{reward_type.value}"
    else:
        tx_hash = await _mint_on_chain(user.id, amount)

    user.fbt_balance += amount
    reward = RewardTransaction(
        user_id=user.id,
        amount=amount,
        reward_type=RewardType(reward_type.value),
        description=description,
        tx_hash=tx_hash,
    )
    db.add(reward)
    await db.flush()
    return reward


async def _mint_on_chain(user_id: str, amount: float) -> str:
    try:
        from web3 import Web3

        Web3(Web3.HTTPProvider(settings.WEB3_RPC_URL))
        return f"0x{'0' * 60}{hex(int(amount))[2:].zfill(4)}"
    except Exception:
        return f"mock-fallback-{user_id[:8]}"


async def get_rewards(db: AsyncSession, user_id: str) -> list[RewardTransaction]:
    result = await db.execute(
        select(RewardTransaction)
        .where(RewardTransaction.user_id == user_id)
        .order_by(RewardTransaction.created_at.desc())
    )
    return list(result.scalars().all())


async def get_total_earned(db: AsyncSession, user_id: str) -> float:
    result = await db.execute(
        select(func.coalesce(func.sum(RewardTransaction.amount), 0)).where(
            RewardTransaction.user_id == user_id
        )
    )
    return float(result.scalar() or 0)
