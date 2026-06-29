# --------------------------------------------------------
# File: server/app/services/goal_service.py
# Purpose: Savings Goals Services & Logic
# Responsibilities: Calculates target saving targets based on deadline schedules,
#                   manages goal updates, triggers reward minting upon goal completion.
# Author: Srihan Raj Guduru
# --------------------------------------------------------

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import GoalCreate, GoalUpdate
from app.models.user import Goal, GoalStatus, Notification, NotificationType, User
from app.services.reward_service import REWARD_AMOUNTS, RewardTypeEnum, mint_reward


def calculate_monthly_target(target_amount: float, current_amount: float, deadline: datetime | None) -> float:
    """
    Calculates the monthly savings target needed to reach a goal.

    If no deadline is set, defaults to a 12-month payoff schedule.
    Otherwise, divides the remaining amount by the number of months until the deadline.
    """
    remaining = max(target_amount - current_amount, 0)
    if remaining == 0:
        return 0.0
    if deadline is None:
        return remaining / 12
    now = datetime.now(UTC)
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=UTC)
    months = max((deadline.year - now.year) * 12 + (deadline.month - now.month), 1)
    return remaining / months


async def create_goal(db: AsyncSession, user: User, data: GoalCreate) -> Goal:
    monthly_target = calculate_monthly_target(data.target_amount, data.current_amount, data.deadline)
    goal = Goal(
        user_id=user.id,
        name=data.name,
        target_amount=data.target_amount,
        current_amount=data.current_amount,
        monthly_target=monthly_target,
        deadline=data.deadline,
    )
    db.add(goal)
    await db.flush()
    return goal


async def get_goals(db: AsyncSession, user_id: str) -> list[Goal]:
    result = await db.execute(select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc()))
    return list(result.scalars().all())


async def get_goal(db: AsyncSession, user_id: str, goal_id: str) -> Goal | None:
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id))
    return result.scalar_one_or_none()


async def update_goal(db: AsyncSession, user: User, goal: Goal, data: GoalUpdate) -> Goal:
    if data.name is not None:
        goal.name = data.name
    if data.target_amount is not None:
        goal.target_amount = data.target_amount
    if data.current_amount is not None:
        goal.current_amount = data.current_amount
    if data.deadline is not None:
        goal.deadline = data.deadline
    if data.status is not None:
        goal.status = data.status

    goal.monthly_target = calculate_monthly_target(goal.target_amount, goal.current_amount, goal.deadline)

    if goal.current_amount >= goal.target_amount and goal.status != GoalStatus.COMPLETED:
        goal.status = GoalStatus.COMPLETED
        await _complete_goal(db, user, goal)

    await db.flush()
    return goal


async def _complete_goal(db: AsyncSession, user: User, goal: Goal) -> None:
    notif = Notification(
        user_id=user.id,
        title="Goal completed!",
        message=f"Congratulations! You reached your goal: {goal.name}",
        notification_type=NotificationType.GOAL_COMPLETED,
    )
    db.add(notif)
    await mint_reward(
        db, user, REWARD_AMOUNTS[RewardTypeEnum.GOAL], RewardTypeEnum.GOAL,
        f"Goal completed: {goal.name}",
    )


async def delete_goal(db: AsyncSession, goal: Goal) -> None:
    await db.delete(goal)
    await db.flush()
