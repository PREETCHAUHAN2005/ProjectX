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
    severity: str | None = None

    model_config = {"populate_by_name": True}


class TimelineBucket(BaseModel):
    timestamp: str
    count: int
    average_sentiment: float
    top_emotions: list[EmotionScore]
    # IMPLEMENTATION: split volume so the dashboard can chart posts vs comments.
    post_count: int = 0
    comment_count: int = 0


class TimelineResponse(BaseModel):
    buckets: list[TimelineBucket]


class NetworkGraphQuery(BaseModel):
    min_centrality: float | None = None
    min_weight: float | None = None
    topic: str | None = None
    severity: str | None = None


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
    # IMPLEMENTATION extras for the demo dashboard (not source-confirmed WS fields).
    topic_id: str | None = None
    topic_name: str | None = None
    severity: str | None = None
    thread_role: str | None = None
    in_reply_to: str | None = None
    polarity: Polarity | None = None
    emotions: list[EmotionScore] | None = None
    analytics: dict | None = None


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
    posts: int = 0
    emotion_backend: str = "unknown"
    demo_mode: bool = False
    ingest_source: str = "idle"
    websocket_clients: int = 0


class FeedPost(NewPostPayload):
    """Recent-feed row. Analytics is an implementation extension of event:new_post."""

    topic_name: str | None = None
    severity: str | None = None
    analytics: dict | None = None


class RecentFeedResponse(BaseModel):
    posts: list[FeedPost]


class IngestRequest(BaseModel):
    query: str | None = None
    limit: int = Field(default=12, ge=1, le=50)


class IngestResponse(BaseModel):
    accepted: int
    source: str
    query: str | None = None


class NlpPredictRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class NlpPredictResponse(BaseModel):
    emotions: list[EmotionScore]
    polarity: Polarity
    backend: str
