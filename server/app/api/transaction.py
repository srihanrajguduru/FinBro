from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser
from app.core.database import get_db
from app.models.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionSummary,
    TransactionUpdate,
)
from app.services import transaction_service as svc

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionResponse])
async def list_transactions(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await svc.get_transactions(db, user.id)


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(data: TransactionCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    try:
        return await svc.create_transaction(db, user, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/summary", response_model=TransactionSummary)
async def summary(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await svc.get_summary(db, user)


@router.get("/{tx_id}", response_model=TransactionResponse)
async def get_transaction(tx_id: str, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    tx = await svc.get_transaction(db, user.id, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx


@router.put("/{tx_id}", response_model=TransactionResponse)
async def update_transaction(
    tx_id: str, data: TransactionUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    tx = await svc.get_transaction(db, user.id, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return await svc.update_transaction(db, user, tx, data)


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(tx_id: str, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    tx = await svc.get_transaction(db, user.id, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    await svc.delete_transaction(db, tx)
