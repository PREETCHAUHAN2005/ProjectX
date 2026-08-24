from fastapi import APIRouter, Query

from app.schemas.contracts import TrendingResponse
from app.services.analytics import AnalyticsService

router = APIRouter()
_service = AnalyticsService()


@router.get("/trending", response_model=TrendingResponse)
async def trending(limit: int = Query(default=20, ge=1, le=100)) -> TrendingResponse:
    return _service.trending(limit)
