"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-06-29
"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("user_type", sa.Enum("student", "professional", name="usertype"), nullable=False),
        sa.Column("monthly_salary", sa.Float(), nullable=False, server_default="0"),
        sa.Column("monthly_spending_limit", sa.Float(), nullable=True),
        sa.Column("onboarding_complete", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("fbt_balance", sa.Float(), nullable=False, server_default="0"),
        sa.Column("refresh_token", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("transaction_type", sa.Enum("income", "expense", name="transactiontype"), nullable=False),
        sa.Column("category", sa.Enum(
            "food", "transport", "entertainment", "shopping", "bills",
            "health", "education", "savings", "income", "other", name="transactioncategory"
        ), nullable=False),
        sa.Column("description", sa.String(500), nullable=False, server_default=""),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])

    op.create_table(
        "goals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("target_amount", sa.Float(), nullable=False),
        sa.Column("current_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("monthly_target", sa.Float(), nullable=False, server_default="0"),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Enum("active", "completed", "paused", name="goalstatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_goals_user_id", "goals", ["user_id"])

    op.create_table(
        "debts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("balance", sa.Float(), nullable=False),
        sa.Column("interest_rate", sa.Float(), nullable=False),
        sa.Column("minimum_payment", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_debts_user_id", "debts", ["user_id"])

    op.create_table(
        "retirement_projections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("current_age", sa.Integer(), nullable=False),
        sa.Column("retirement_age", sa.Integer(), nullable=False),
        sa.Column("current_savings", sa.Float(), nullable=False),
        sa.Column("monthly_contribution", sa.Float(), nullable=False),
        sa.Column("annual_return_rate", sa.Float(), nullable=False),
        sa.Column("projected_balance", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_retirement_projections_user_id", "retirement_projections", ["user_id"])

    op.create_table(
        "reward_transactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("reward_type", sa.Enum(
            "goal", "monthly_savings", "debt_milestone", "manual", name="rewardtype"
        ), nullable=False),
        sa.Column("description", sa.String(500), nullable=False, server_default=""),
        sa.Column("tx_hash", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reward_transactions_user_id", "reward_transactions", ["user_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("notification_type", sa.Enum(
            "spending_warning", "goal_completed", "reward_earned",
            "debt_milestone", "general", name="notificationtype"
        ), nullable=False),
        sa.Column("read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("reward_transactions")
    op.drop_table("retirement_projections")
    op.drop_table("debts")
    op.drop_table("goals")
    op.drop_table("transactions")
    op.drop_table("users")
