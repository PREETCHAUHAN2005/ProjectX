from fastapi import APIRouter, Query

from app.schemas.contracts import (
    DemographicsResponse,
    NetworkGraphQuery,
    NetworkGraphResponse,
    TimelineQuery,
    TimelineResponse,
)
from app.services.analytics import AnalyticsService

router = APIRouter()
_service = AnalyticsService()


@router.get("/timeline", response_model=TimelineResponse)
async def timeline(
    topic: str | None = None,
    bucket: str = "hour",
    min_from: str | None = Query(default=None, alias="from"),
    min_to: str | None = Query(default=None, alias="to"),
    severity: str | None = None,
) -> TimelineResponse:
    if bucket not in ("hour", "day"):
        bucket = "hour"
    query = TimelineQuery.model_validate(
        {
            "from": min_from,
            "to": min_to,
            "bucket": bucket,
            "topic": topic,
            "severity": severity,
        }
    )
    return _service.timeline(query)


@router.get("/network-graph", response_model=NetworkGraphResponse)
async def network_graph(
    topic: str | None = None,
    min_centrality: float | None = None,
    min_weight: float | None = None,
    severity: str | None = None,
) -> NetworkGraphResponse:
    query = NetworkGraphQuery(
        topic=topic,
        min_centrality=min_centrality,
        min_weight=min_weight,
        severity=severity,
    )
    return _service.network_graph(query)


@router.get("/demographics", response_model=DemographicsResponse)
async def demographics(
    topic: str | None = None,
    severity: str | None = None,
) -> DemographicsResponse:
    return _service.demographics(topic, severity)
