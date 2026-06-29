from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser
from app.core.database import get_db
from app.models.schemas import RewardBalanceResponse, RewardResponse
from app.services import reward_service as svc

router = APIRouter(prefix="/rewards", tags=["rewards"])


@router.get("", response_model=list[RewardResponse])
async def list_rewards(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await svc.get_rewards(db, user.id)


@router.get("/balance", response_model=RewardBalanceResponse)
async def reward_balance(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    transactions = await svc.get_rewards(db, user.id)
    total = await svc.get_total_earned(db, user.id)
    return RewardBalanceResponse(
        fbt_balance=user.fbt_balance,
        total_earned=total,
        transactions=transactions,
    )
