import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1
from app.core.config import settings
from app.core.exceptions import install_exception_handlers
from app.schemas.contracts import HealthResponse
from app.ws.gateway import router as ws_router

logger = logging.getLogger(__name__)


async def _demo_ticker(stop: asyncio.Event) -> None:
    from app.services.demo_seed import pop_ticker_document
    from app.services.ingest import persist_and_emit

    delay = max(float(settings.demo_tick_seconds), 0.5)
    while True:
        try:
            await asyncio.wait_for(stop.wait(), timeout=delay)
            return
        except asyncio.TimeoutError:
            document = pop_ticker_document()
            if document is None:
                continue
            try:
                await persist_and_emit(document)
            except Exception:
                logger.exception("Demo ticker failed to persist a comment")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    stop = asyncio.Event()
    tick_task: asyncio.Task[None] | None = None
    if settings.demo_seed:
        from app.services.demo_seed import load_demo_seed
        from app.services.ingest import persist_to_stores

        load_demo_seed(persist=lambda document: persist_to_stores(document))
        tick_task = asyncio.create_task(_demo_ticker(stop))
    yield
    stop.set()
    if tick_task is not None:
        await tick_task


app = FastAPI(
    title="ProjectX Social Intelligence API",
    version="0.1.0",
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
    return HealthResponse(status="ok")
