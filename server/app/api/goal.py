from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser
from app.core.database import get_db
from app.models.schemas import GoalCreate, GoalResponse, GoalUpdate
from app.services import goal_service as svc

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=list[GoalResponse])
async def list_goals(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await svc.get_goals(db, user.id)


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(data: GoalCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await svc.create_goal(db, user, data)


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(goal_id: str, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    goal = await svc.get_goal(db, user.id, goal_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str, data: GoalUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    goal = await svc.get_goal(db, user.id, goal_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return await svc.update_goal(db, user, goal, data)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(goal_id: str, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    goal = await svc.get_goal(db, user.id, goal_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    await svc.delete_goal(db, goal)
