# --------------------------------------------------------
# File: server/app/services/prediction_service.py
# Purpose: Financial Forecasting & Projection Services
# Responsibilities: Implements compound interest calculations and creates retirement
#                   projection records for users.
# Author: Srihan Raj Guduru
# --------------------------------------------------------

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import RetirementRequest, RetirementResponse
from app.models.user import RetirementProjection, User


def compound_interest_projection(
    current_savings: float,
    monthly_contribution: float,
    annual_return_rate: float,
    years: int,
) -> float:
    """
    Computes the future value of a savings account with monthly compounding.

    Formula used: FV = PV*(1+r)^n + PMT * [((1+r)^n - 1) / r]
    where:
    - PV = current savings
    - PMT = monthly contribution
    - r = monthly interest rate
    - n = total compounding periods (months)
    """
    if years <= 0:
        return current_savings

    monthly_rate = annual_return_rate / 100 / 12
    n = years * 12

    if monthly_rate == 0:
        return current_savings + monthly_contribution * n

    fv_principal = current_savings * ((1 + monthly_rate) ** n)
    fv_contributions = monthly_contribution * (((1 + monthly_rate) ** n - 1) / monthly_rate)
    return round(fv_principal + fv_contributions, 2)


async def create_projection(db: AsyncSession, user: User, data: RetirementRequest) -> RetirementProjection:
    years = data.retirement_age - data.current_age
    projected = compound_interest_projection(
        data.current_savings,
        data.monthly_contribution,
        data.annual_return_rate,
        years,
    )
    projection = RetirementProjection(
        user_id=user.id,
        current_age=data.current_age,
        retirement_age=data.retirement_age,
        current_savings=data.current_savings,
        monthly_contribution=data.monthly_contribution,
        annual_return_rate=data.annual_return_rate,
        projected_balance=projected,
    )
    db.add(projection)
    await db.flush()
    return projection


async def get_projections(db: AsyncSession, user_id: str) -> list[RetirementProjection]:
    result = await db.execute(
        select(RetirementProjection)
        .where(RetirementProjection.user_id == user_id)
        .order_by(RetirementProjection.created_at.desc())
    )
    return list(result.scalars().all())


def to_response(projection: RetirementProjection) -> RetirementResponse:
    return RetirementResponse(
        id=projection.id,
        user_id=projection.user_id,
        current_age=projection.current_age,
        retirement_age=projection.retirement_age,
        current_savings=projection.current_savings,
        monthly_contribution=projection.monthly_contribution,
        annual_return_rate=projection.annual_return_rate,
        projected_balance=projection.projected_balance,
        years_to_retirement=projection.retirement_age - projection.current_age,
        created_at=projection.created_at,
    )
