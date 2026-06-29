from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser
from app.core.database import get_db
from app.models.schemas import (
    AmortizationRequest,
    AmortizationResponse,
    DebtCreate,
    DebtResponse,
    DebtUpdate,
    PayoffSimulationRequest,
    PayoffSimulationResponse,
)
from app.services import debt_service as svc

router = APIRouter(prefix="/debts", tags=["debts"])


@router.get("", response_model=list[DebtResponse])
async def list_debts(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await svc.get_debts(db, user.id)


@router.post("", response_model=DebtResponse, status_code=status.HTTP_201_CREATED)
async def create_debt(data: DebtCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await svc.create_debt(db, user.id, data)


@router.get("/{debt_id}", response_model=DebtResponse)
async def get_debt(debt_id: str, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    debt = await svc.get_debt(db, user.id, debt_id)
    if not debt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debt not found")
    return debt


@router.put("/{debt_id}", response_model=DebtResponse)
async def update_debt(
    debt_id: str, data: DebtUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    debt = await svc.get_debt(db, user.id, debt_id)
    if not debt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debt not found")
    return await svc.update_debt(db, debt, data)


@router.delete("/{debt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_debt(debt_id: str, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    debt = await svc.get_debt(db, user.id, debt_id)
    if not debt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debt not found")
    await svc.delete_debt(db, debt)


@router.post("/payoff/simulate", response_model=PayoffSimulationResponse)
async def simulate_payoff(
    data: PayoffSimulationRequest, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    debts = await svc.get_debts(db, user.id)
    if not debts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No debts to simulate")
    return svc.simulate_payoff(debts, data)


@router.post("/amortization", response_model=AmortizationResponse)
async def amortization(data: AmortizationRequest):
    try:
        return svc.single_debt_amortization(data.balance, data.interest_rate, data.monthly_payment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
