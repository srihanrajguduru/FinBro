from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser
from app.core.database import get_db
from app.models.schemas import ExpenseCreate, ExpenseResponse, SpendingLimitStatus
from app.services import notification_service as svc

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpenseResponse])
async def list_expenses(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    from app.models.user import TransactionType
    from app.services.transaction_service import get_transactions

    txs = await get_transactions(db, user.id)
    return [
        ExpenseResponse(
            id=t.id, user_id=t.user_id, amount=t.amount, category=t.category,
            description=t.description, date=t.date, created_at=t.created_at,
        )
        for t in txs if t.transaction_type == TransactionType.EXPENSE
    ]


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(data: ExpenseCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    try:
        tx = await svc.create_expense(db, user, data)
        return ExpenseResponse(
            id=tx.id, user_id=tx.user_id, amount=tx.amount, category=tx.category,
            description=tx.description, date=tx.date, created_at=tx.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/limit-status", response_model=SpendingLimitStatus)
async def limit_status(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await svc.get_spending_limit_status(db, user)
