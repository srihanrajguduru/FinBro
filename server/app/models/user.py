# --------------------------------------------------------
# File: server/app/models/user.py
# Purpose: SQLAlchemy Database Models & Schemas
# Responsibilities: Defines database schemas (users, transactions, goals, debts, etc.)
#                   and custom type mappers for SQL compatibility.
# Author: Srihan Raj Guduru
# --------------------------------------------------------

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserType(str, enum.Enum):
    STUDENT = "student"
    PROFESSIONAL = "professional"


class TransactionCategory(str, enum.Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    BILLS = "bills"
    HEALTH = "health"
    EDUCATION = "education"
    SAVINGS = "savings"
    INCOME = "income"
    OTHER = "other"


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class DebtStrategy(str, enum.Enum):
    AVALANCHE = "avalanche"
    SNOWBALL = "snowball"


class RewardType(str, enum.Enum):
    GOAL = "goal"
    MONTHLY_SAVINGS = "monthly_savings"
    DEBT_MILESTONE = "debt_milestone"
    MANUAL = "manual"


class NotificationType(str, enum.Enum):
    SPENDING_WARNING = "spending_warning"
    GOAL_COMPLETED = "goal_completed"
    REWARD_EARNED = "reward_earned"
    DEBT_MILESTONE = "debt_milestone"
    GENERAL = "general"


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return str(uuid.uuid4())


def _db_enum(enum_cls):
    return Enum(enum_cls, values_callable=lambda x: [e.value for e in x])


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255), default="")
    user_type: Mapped[UserType] = mapped_column(_db_enum(UserType), default=UserType.STUDENT)
    monthly_salary: Mapped[float] = mapped_column(Float, default=0.0)
    monthly_spending_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    fbt_balance: Mapped[float] = mapped_column(Float, default=0.0)
    refresh_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    goals: Mapped[list["Goal"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    debts: Mapped[list["Debt"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    retirement_projections: Mapped[list["RetirementProjection"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    reward_transactions: Mapped[list["RewardTransaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    transaction_type: Mapped[TransactionType] = mapped_column(_db_enum(TransactionType))
    category: Mapped[TransactionCategory] = mapped_column(_db_enum(TransactionCategory))
    description: Mapped[str] = mapped_column(String(500), default="")
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="transactions")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    target_amount: Mapped[float] = mapped_column(Float)
    current_amount: Mapped[float] = mapped_column(Float, default=0.0)
    monthly_target: Mapped[float] = mapped_column(Float, default=0.0)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[GoalStatus] = mapped_column(_db_enum(GoalStatus), default=GoalStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    user: Mapped["User"] = relationship(back_populates="goals")


class Debt(Base):
    __tablename__ = "debts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    balance: Mapped[float] = mapped_column(Float)
    interest_rate: Mapped[float] = mapped_column(Float)
    minimum_payment: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    user: Mapped["User"] = relationship(back_populates="debts")


class RetirementProjection(Base):
    __tablename__ = "retirement_projections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    current_age: Mapped[int] = mapped_column(Integer)
    retirement_age: Mapped[int] = mapped_column(Integer)
    current_savings: Mapped[float] = mapped_column(Float)
    monthly_contribution: Mapped[float] = mapped_column(Float)
    annual_return_rate: Mapped[float] = mapped_column(Float, default=7.0)
    projected_balance: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="retirement_projections")


class RewardTransaction(Base):
    __tablename__ = "reward_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    reward_type: Mapped[RewardType] = mapped_column(_db_enum(RewardType))
    description: Mapped[str] = mapped_column(String(500), default="")
    tx_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="reward_transactions")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    notification_type: Mapped[NotificationType] = mapped_column(_db_enum(NotificationType))
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="notifications")
