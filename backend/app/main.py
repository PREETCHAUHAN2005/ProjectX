from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1
from app.core.config import settings
from app.core.exceptions import install_exception_handlers
from app.schemas.contracts import HealthResponse
from app.ws.gateway import router as ws_router

app = FastAPI(
    title="ProjectX Social Intelligence API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

install_exception_handlers(app)
app.include_router(api_v1, prefix="/api/v1")
app.include_router(ws_router)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """IMPLEMENTATION extra — not a confirmed product API."""
    return HealthResponse(status="ok")
