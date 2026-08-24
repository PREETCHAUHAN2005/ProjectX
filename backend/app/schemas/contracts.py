from typing import Literal

from pydantic import BaseModel, Field

Polarity = Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]
Platform = Literal["telegram", "x"]
BucketSize = Literal["hour", "day"]
WsEventName = Literal["event:new_post", "event:trend_spike", "event:graph_delta"]


class EmotionScore(BaseModel):
    label: str
    score: float


class TimelineQuery(BaseModel):
    """IMPLEMENTATION query params — not source-confirmed names."""

    from_ts: str | None = Field(default=None, alias="from")
    to_ts: str | None = Field(default=None, alias="to")
    bucket: BucketSize = "hour"
    topic: str | None = None

    model_config = {"populate_by_name": True}


class TimelineBucket(BaseModel):
    timestamp: str
    count: int
    average_sentiment: float
    top_emotions: list[EmotionScore]


class TimelineResponse(BaseModel):
    buckets: list[TimelineBucket]


class NetworkGraphQuery(BaseModel):
    min_centrality: float | None = None
    min_weight: float | None = None
    topic: str | None = None


class GraphNode(BaseModel):
    id: str
    handle: str
    platform: str
    pagerank: float
    community: str


class GraphLink(BaseModel):
    source: str
    target: str
    type: str
    timestamp: str
    weight: float


class NetworkGraphResponse(BaseModel):
    nodes: list[GraphNode]
    links: list[GraphLink]


class DemographicSlice(BaseModel):
    key: str
    count: int


class DemographicsResponse(BaseModel):
    country: list[DemographicSlice]
    language: list[DemographicSlice]
    profession: list[DemographicSlice]


class TrendingTopic(BaseModel):
    topic_id: str
    topic_name: str
    velocity: float
    acceleration: float
    sample_size: int


class TrendingResponse(BaseModel):
    topics: list[TrendingTopic]


class Author(BaseModel):
    user_id: str
    handle: str
    bio: str | None = None
    follower_count: int | None = None


class PostContent(BaseModel):
    raw_text: str
    hashtags: list[str] | None = None
    language: str | None = None


class NewPostPayload(BaseModel):
    platform: Platform
    external_id: str
    timestamp: str
    author: Author
    content: PostContent


class TrendSpikePayload(BaseModel):
    topic_id: str
    topic_name: str
    velocity: float
    sample_size: int


class GraphDeltaPayload(BaseModel):
    nodes: list[GraphNode]
    links: list[GraphLink]


class WsEnvelope(BaseModel):
    """IMPLEMENTATION envelope. Event names are source-confirmed."""

    event: WsEventName
    payload: dict


class WsFilterCriteria(BaseModel):
    type: Literal["filter"]
    topic: str | None = None
    time_window: dict | None = None
    severity: str | None = None


class HealthResponse(BaseModel):
    """IMPLEMENTATION extra — not a confirmed product API."""

    status: str
