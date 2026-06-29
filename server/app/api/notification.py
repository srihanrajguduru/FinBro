from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser
from app.core.database import get_db
from app.models.schemas import ChatRequest, ChatResponse, NotificationResponse
from app.services import notification_service as svc

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await svc.get_notifications(db, user.id)


@router.put("/{notif_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notif_id: str, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    notif = await svc.mark_read(db, user.id, notif_id)
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notif


@router.put("/read-all")
async def mark_all_notifications_read(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    count = await svc.mark_all_read(db, user.id)
    return {"marked_read": count}


chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post("", response_model=ChatResponse)
async def chat(data: ChatRequest, user: CurrentUser):
    return await svc.process_chat(data)
