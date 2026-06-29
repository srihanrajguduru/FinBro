from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import (
    DebtStrategy,
    GoalStatus,
    NotificationType,
    RewardType,
    TransactionCategory,
    TransactionType,
    UserType,
)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = ""


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    user_type: UserType
    monthly_salary: float
    monthly_spending_limit: float | None
    onboarding_complete: bool
    fbt_balance: float
    created_at: datetime


class OnboardingRequest(BaseModel):
    user_type: UserType
    monthly_salary: float = Field(gt=0)
    monthly_spending_limit: float | None = None


class TransactionCreate(BaseModel):
    amount: float = Field(gt=0)
    transaction_type: TransactionType
    category: TransactionCategory
    description: str = ""
    date: datetime | None = None


class TransactionUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    transaction_type: TransactionType | None = None
    category: TransactionCategory | None = None
    description: str | None = None
    date: datetime | None = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    amount: float
    transaction_type: TransactionType
    category: TransactionCategory
    description: str
    date: datetime
    created_at: datetime


class TransactionSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    savings_target: float
    by_category: dict[str, float]


class GoalCreate(BaseModel):
    name: str
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    deadline: datetime | None = None


class GoalUpdate(BaseModel):
    name: str | None = None
    target_amount: float | None = Field(default=None, gt=0)
    current_amount: float | None = Field(default=None, ge=0)
    deadline: datetime | None = None
    status: GoalStatus | None = None


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    target_amount: float
    current_amount: float
    monthly_target: float
    deadline: datetime | None
    status: GoalStatus
    created_at: datetime
    updated_at: datetime


class DebtCreate(BaseModel):
    name: str
    balance: float = Field(gt=0)
    interest_rate: float = Field(ge=0)
    minimum_payment: float = Field(gt=0)


class DebtUpdate(BaseModel):
    name: str | None = None
    balance: float | None = Field(default=None, gt=0)
    interest_rate: float | None = Field(default=None, ge=0)
    minimum_payment: float | None = Field(default=None, gt=0)


class DebtResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    balance: float
    interest_rate: float
    minimum_payment: float
    created_at: datetime
    updated_at: datetime


class PayoffSimulationRequest(BaseModel):
    strategy: DebtStrategy
    extra_payment: float = Field(default=0, ge=0)


class PayoffMonth(BaseModel):
    month: int
    debt_name: str
    payment: float
    interest: float
    principal: float
    remaining_balance: float


class PayoffSimulationResponse(BaseModel):
    strategy: DebtStrategy
    total_months: int
    total_interest: float
    total_paid: float
    schedule: list[PayoffMonth]
    debts_eliminated: list[str]


class AmortizationRequest(BaseModel):
    balance: float = Field(gt=0)
    interest_rate: float = Field(ge=0)
    monthly_payment: float = Field(gt=0)


class AmortizationResponse(BaseModel):
    months_to_payoff: int
    total_interest: float
    total_paid: float


class RetirementRequest(BaseModel):
    current_age: int = Field(ge=18, le=100)
    retirement_age: int = Field(ge=40, le=100)
    current_savings: float = Field(ge=0)
    monthly_contribution: float = Field(ge=0)
    annual_return_rate: float = Field(default=7.0, ge=0, le=30)


class RetirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    current_age: int
    retirement_age: int
    current_savings: float
    monthly_contribution: float
    annual_return_rate: float
    projected_balance: float
    years_to_retirement: int
    created_at: datetime


class RewardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    amount: float
    reward_type: RewardType
    description: str
    tx_hash: str | None
    created_at: datetime


class RewardBalanceResponse(BaseModel):
    fbt_balance: float
    total_earned: float
    transactions: list[RewardResponse]


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    message: str
    notification_type: NotificationType
    read: bool
    created_at: datetime


class SpendingLimitStatus(BaseModel):
    limit: float
    spent: float
    remaining: float
    percentage: float
    warning_level: str  # "green", "yellow", "red", "blocked"


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    intent: str


class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    category: TransactionCategory
    description: str = ""
    date: datetime | None = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    amount: float
    category: TransactionCategory
    description: str
    date: datetime
    created_at: datetime
