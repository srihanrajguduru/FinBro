# --------------------------------------------------------
# File: server/app/services/debt_service.py
# Purpose: Debt Repayment & Simulation Services
# Responsibilities: Implements the debt payoff calculators for individual
#                   amortization schedules and multi-debt strategy simulations (Avalanche vs Snowball).
# Author: Srihan Raj Guduru
# --------------------------------------------------------

import math

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import (
    AmortizationResponse,
    DebtCreate,
    DebtUpdate,
    PayoffMonth,
    PayoffSimulationRequest,
    PayoffSimulationResponse,
)
from app.models.user import Debt, DebtStrategy

MAX_SIMULATION_MONTHS = 600


async def create_debt(db: AsyncSession, user_id: str, data: DebtCreate) -> Debt:
    debt = Debt(
        user_id=user_id,
        name=data.name,
        balance=data.balance,
        interest_rate=data.interest_rate,
        minimum_payment=data.minimum_payment,
    )
    db.add(debt)
    await db.flush()
    return debt


async def get_debts(db: AsyncSession, user_id: str) -> list[Debt]:
    result = await db.execute(select(Debt).where(Debt.user_id == user_id).order_by(Debt.created_at.desc()))
    return list(result.scalars().all())


async def get_debt(db: AsyncSession, user_id: str, debt_id: str) -> Debt | None:
    result = await db.execute(select(Debt).where(Debt.id == debt_id, Debt.user_id == user_id))
    return result.scalar_one_or_none()


async def update_debt(db: AsyncSession, debt: Debt, data: DebtUpdate) -> Debt:
    if data.name is not None:
        debt.name = data.name
    if data.balance is not None:
        debt.balance = data.balance
    if data.interest_rate is not None:
        debt.interest_rate = data.interest_rate
    if data.minimum_payment is not None:
        debt.minimum_payment = data.minimum_payment
    await db.flush()
    return debt


async def delete_debt(db: AsyncSession, debt: Debt) -> None:
    await db.delete(debt)
    await db.flush()


def single_debt_amortization(balance: float, annual_rate: float, monthly_payment: float) -> AmortizationResponse:
    """Closed-form amortization with month-by-month verification."""
    if monthly_payment <= 0:
        raise ValueError("Monthly payment must be positive")

    monthly_rate = annual_rate / 100 / 12
    if monthly_rate == 0:
        months = math.ceil(balance / monthly_payment)
        total_paid = months * monthly_payment
        return AmortizationResponse(
            months_to_payoff=months,
            total_interest=total_paid - balance,
            total_paid=total_paid,
        )

    if monthly_payment <= balance * monthly_rate:
        raise ValueError("Payment too low to cover interest")

    months = math.ceil(
        -math.log(1 - (balance * monthly_rate) / monthly_payment) / math.log(1 + monthly_rate)
    )

    remaining = balance
    total_interest = 0.0
    for _ in range(months):
        interest = remaining * monthly_rate
        principal = monthly_payment - interest
        total_interest += interest
        remaining -= principal
        if remaining <= 0.01:
            break

    total_paid = balance + total_interest
    return AmortizationResponse(
        months_to_payoff=months,
        total_interest=round(total_interest, 2),
        total_paid=round(total_paid, 2),
    )


def simulate_payoff(debts: list[Debt], request: PayoffSimulationRequest) -> PayoffSimulationResponse:
    """
    Performs a month-by-month debt repayment simulation up to a 600-month cap.

    Supports:
    - Debt Avalanche: Prioritizes debts with the highest interest rates.
    - Debt Snowball: Prioritizes debts with the lowest remaining balances.

    Distributes extra monthly payments on top of individual minimum payments.
    """
    debt_states = [
        {
            "id": d.id,
            "name": d.name,
            "balance": d.balance,
            "rate": d.interest_rate,
            "min_payment": d.minimum_payment,
        }
        for d in debts
    ]

    if request.strategy == DebtStrategy.AVALANCHE:
        debt_states.sort(key=lambda d: d["rate"], reverse=True)
    else:
        debt_states.sort(key=lambda d: d["balance"])

    schedule: list[PayoffMonth] = []
    total_interest = 0.0
    total_paid = 0.0
    eliminated: list[str] = []
    month = 0

    while any(d["balance"] > 0.01 for d in debt_states) and month < MAX_SIMULATION_MONTHS:
        month += 1
        active = [d for d in debt_states if d["balance"] > 0.01]

        for d in active:
            monthly_rate = d["rate"] / 100 / 12
            interest = d["balance"] * monthly_rate
            d["balance"] += interest
            total_interest += interest

        total_min = sum(d["min_payment"] for d in active)
        available = total_min + request.extra_payment

        if request.strategy == DebtStrategy.AVALANCHE:
            target_order = sorted(active, key=lambda d: d["rate"], reverse=True)
        else:
            target_order = sorted(active, key=lambda d: d["balance"])

        for d in active:
            payment = min(d["min_payment"], d["balance"], available)
            d["balance"] -= payment
            available -= payment
            total_paid += payment
            schedule.append(
                PayoffMonth(
                    month=month,
                    debt_name=d["name"],
                    payment=round(payment, 2),
                    interest=round(d["rate"] / 100 / 12 * (d["balance"] + payment), 2),
                    principal=round(payment, 2),
                    remaining_balance=round(max(d["balance"], 0), 2),
                )
            )
            if d["balance"] <= 0.01 and d["name"] not in eliminated:
                eliminated.append(d["name"])
                d["balance"] = 0

        target = next((d for d in target_order if d["balance"] > 0.01), None)
        while available > 0.01 and target:
            payment = min(available, target["balance"])
            target["balance"] -= payment
            available -= payment
            total_paid += payment
            if target["balance"] <= 0.01 and target["name"] not in eliminated:
                eliminated.append(target["name"])
                target["balance"] = 0
            target = next((d for d in target_order if d["balance"] > 0.01), None)

    return PayoffSimulationResponse(
        strategy=request.strategy,
        total_months=month,
        total_interest=round(total_interest, 2),
        total_paid=round(total_paid, 2),
        schedule=schedule[:100],
        debts_eliminated=eliminated,
    )
