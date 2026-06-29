from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser
from app.core.database import get_db
from app.models.schemas import RetirementRequest, RetirementResponse
from app.services import prediction_service as svc

router = APIRouter(prefix="/predict", tags=["predictions"])


@router.post("/retirement", response_model=RetirementResponse, status_code=201)
async def create_retirement_projection(
    data: RetirementRequest, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    projection = await svc.create_projection(db, user, data)
    return svc.to_response(projection)


@router.get("/retirement", response_model=list[RetirementResponse])
async def list_retirement_projections(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    projections = await svc.get_projections(db, user.id)
    return [svc.to_response(p) for p in projections]
