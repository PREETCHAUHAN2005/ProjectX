from fastapi import APIRouter

from app.api.v1 import analytics, topics

api_v1 = APIRouter()
api_v1.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_v1.include_router(topics.router, prefix="/topics", tags=["topics"])
