from fastapi import APIRouter

from app.core.config import settings
from app.schemas.contracts import (
    IngestRequest,
    IngestResponse,
    NlpPredictRequest,
    NlpPredictResponse,
    RecentFeedResponse,
)
from app.services.live import get_runtime, recent_feed_payloads

router = APIRouter()


@router.get("/feed/recent", response_model=RecentFeedResponse)
async def recent_feed(limit: int = 40) -> RecentFeedResponse:
    capped = min(max(limit, 1), 80)
    return RecentFeedResponse.model_validate({"posts": recent_feed_payloads(capped)})


@router.post("/ingest/run", response_model=IngestResponse)
async def ingest_run(body: IngestRequest | None = None) -> IngestResponse:
    payload = body or IngestRequest()
    runtime = get_runtime()
    accepted, source = await runtime.fetch_posts(query=payload.query, limit=payload.limit)
    return IngestResponse(
        accepted=accepted,
        source=source,
        query=payload.query or settings.x_query,
    )


@router.post("/nlp/predict", response_model=NlpPredictResponse)
async def nlp_predict(body: NlpPredictRequest) -> NlpPredictResponse:
    result = get_runtime().predict_text(body.text)
    return NlpPredictResponse.model_validate(result)
