from datetime import UTC, datetime, timedelta

import pytest

from app.models.schemas import PayoffSimulationRequest
from app.models.user import Debt, DebtStrategy
from app.services.debt_service import simulate_payoff, single_debt_amortization
from app.services.goal_service import calculate_monthly_target
from app.services.prediction_service import compound_interest_projection


def test_monthly_target_with_deadline():
    deadline = datetime.now(UTC) + timedelta(days=365)
    target = calculate_monthly_target(12000, 2000, deadline)
    assert 800 <= target <= 900


def test_monthly_target_no_deadline():
    target = calculate_monthly_target(12000, 2000, None)
    assert target == pytest.approx(10000 / 12, rel=0.01)


def test_amortization_zero_interest():
    result = single_debt_amortization(1200, 0, 100)
    assert result.months_to_payoff == 12
    assert result.total_interest == pytest.approx(0, abs=1)


def test_amortization_with_interest():
    result = single_debt_amortization(10000, 6, 200)
    assert result.months_to_payoff > 0
    assert result.total_interest > 0


def test_compound_interest():
    result = compound_interest_projection(10000, 500, 7, 30)
    assert result > 10000 + 500 * 30 * 12


def test_payoff_simulation():
    debts = [
        Debt(id="1", user_id="u", name="Card", balance=5000, interest_rate=18, minimum_payment=100),
        Debt(id="2", user_id="u", name="Loan", balance=10000, interest_rate=5, minimum_payment=200),
    ]
    req = PayoffSimulationRequest(strategy=DebtStrategy.AVALANCHE, extra_payment=100)
    result = simulate_payoff(debts, req)
    assert result.total_months > 0
    assert result.total_interest > 0
    assert len(result.debts_eliminated) == 2
