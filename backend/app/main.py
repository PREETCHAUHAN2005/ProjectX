from contextlib import asynccontextmanager

from app.core.paths import ensure_repo_on_path

ensure_repo_on_path()

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1
from app.core.config import settings
from app.core.exceptions import install_exception_handlers
from app.schemas.contracts import HealthResponse
from app.services.live import get_runtime
from app.stores.posts import get_post_store
from app.ws.gateway import hub, router as ws_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    import asyncio

    runtime = get_runtime()
    loop_task = None
    if settings.demo_mode and settings.app_env != "test":
        await runtime.seed_if_empty()
        loop_task = asyncio.create_task(runtime.run_loop())
    try:
        yield
    finally:
        if loop_task is not None:
            loop_task.cancel()
            try:
                await loop_task
            except asyncio.CancelledError:
                pass


app = FastAPI(
    title="ProjectX Social Intelligence API",
    version="0.2.0",
    lifespan=lifespan,
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
    runtime = get_runtime()
    return HealthResponse(
        status="ok",
        posts=get_post_store().count(),
        emotion_backend=settings.emotion_backend,
        demo_mode=settings.demo_mode,
        ingest_source=runtime.ingest_source,
        websocket_clients=hub.client_count,
    )
