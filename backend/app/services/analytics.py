from collections import defaultdict
from datetime import datetime, timezone

from app.schemas.contracts import (
    DemographicSlice,
    DemographicsResponse,
    EmotionScore,
    NetworkGraphQuery,
    NetworkGraphResponse,
    TimelineBucket,
    TimelineQuery,
    TimelineResponse,
    TrendingResponse,
    TrendingTopic,
)
from app.stores.graph import get_graph_store
from app.stores.posts import get_post_store


def _topic_velocity(current_count: int, previous_count: int) -> float:
    """Keep in lockstep with workers.inference.trend_spike.topic_velocity."""
    return current_count / max(previous_count, 1)

# IMPLEMENTATION numeric mapping for timeline average_sentiment.
POLARITY_TO_NUMBER = {"POSITIVE": 1.0, "NEUTRAL": 0.0, "NEGATIVE": -1.0}


def _parse_ts(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _bucket_start(ts: datetime, bucket: str) -> str:
    if bucket == "day":
        aligned = ts.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        aligned = ts.replace(minute=0, second=0, microsecond=0)
    return aligned.isoformat()


class AnalyticsService:
    def timeline(self, query: TimelineQuery) -> TimelineResponse:
        posts = get_post_store().list_posts(
            topic=query.topic,
            from_ts=query.from_ts,
            to_ts=query.to_ts,
            severity=query.severity,
        )
        grouped: dict[str, list[dict]] = defaultdict(list)
        for post in posts:
            try:
                key = _bucket_start(_parse_ts(str(post.get("timestamp") or "")), query.bucket)
            except ValueError:
                continue
            grouped[key].append(post)

        buckets: list[TimelineBucket] = []
        for timestamp in sorted(grouped):
            rows = grouped[timestamp]
            scores = []
            emotion_sums: dict[str, float] = defaultdict(float)
            emotion_n: dict[str, int] = defaultdict(int)
            post_count = 0
            comment_count = 0
            for post in rows:
                analytics = post.get("analytics") or {}
                sentiment = analytics.get("sentiment") or {}
                label = sentiment.get("label")
                if label in POLARITY_TO_NUMBER:
                    scores.append(POLARITY_TO_NUMBER[label])
                role = str(analytics.get("thread_role") or "post")
                if role == "comment":
                    comment_count += 1
                else:
                    post_count += 1
                for emotion in analytics.get("emotions") or []:
                    name = str(emotion.get("label") or "")
                    if not name:
                        continue
                    emotion_sums[name] += float(emotion.get("score") or 0.0)
                    emotion_n[name] += 1
            averaged = [
                EmotionScore(label=name, score=emotion_sums[name] / emotion_n[name])
                for name in emotion_sums
            ]
            averaged.sort(key=lambda item: item.score, reverse=True)
            buckets.append(
                TimelineBucket(
                    timestamp=timestamp,
                    count=len(rows),
                    average_sentiment=(sum(scores) / len(scores)) if scores else 0.0,
                    top_emotions=averaged[:3],
                    post_count=post_count,
                    comment_count=comment_count,
                )
            )
        return TimelineResponse(buckets=buckets)

    def network_graph(self, query: NetworkGraphQuery) -> NetworkGraphResponse:
        nodes, links = get_graph_store().snapshot(
            min_centrality=query.min_centrality,
            min_weight=query.min_weight,
        )
        if query.topic or query.severity:
            posts = get_post_store().list_posts(
                topic=query.topic, severity=query.severity
            )
            allowed = {
                str((post.get("author") or {}).get("user_id") or "") for post in posts
            }
            nodes = [node for node in nodes if node.id in allowed]
            allowed_ids = {node.id for node in nodes}
            links = [
                link
                for link in links
                if link.source in allowed_ids and link.target in allowed_ids
            ]
        return NetworkGraphResponse(nodes=nodes, links=links)

    def demographics(self, topic: str | None, severity: str | None = None) -> DemographicsResponse:
        posts = get_post_store().list_posts(topic=topic, severity=severity)

        def tally(field: str) -> list[DemographicSlice]:
            counts: dict[str, int] = defaultdict(int)
            for post in posts:
                analytics = post.get("analytics") or {}
                demo = analytics.get("demographics") or {}
                if field == "language":
                    value = (post.get("content") or {}).get("language")
                else:
                    value = demo.get(field)
                if isinstance(value, str) and value:
                    counts[value] += 1
            return [
                DemographicSlice(key=key, count=counts[key])
                for key in sorted(counts, key=lambda item: (-counts[item], item))
            ]

        return DemographicsResponse(
            country=tally("inferred_country"),
            language=tally("language"),
            profession=tally("inferred_profession"),
        )

    def trending(self, limit: int) -> TrendingResponse:
        posts = get_post_store().list_posts()
        by_topic_hour: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        names: dict[str, str] = {}
        for post in posts:
            analytics = post.get("analytics") or {}
            topic_id = analytics.get("topic_id")
            topic_name = analytics.get("topic_name")
            if not topic_id and not topic_name:
                continue
            key = str(topic_id or topic_name)
            names[key] = str(topic_name or topic_id)
            try:
                hour = _bucket_start(_parse_ts(str(post.get("timestamp") or "")), "hour")
            except ValueError:
                continue
            by_topic_hour[key][hour] += 1

        topics: list[TrendingTopic] = []
        for topic_id, hours in by_topic_hour.items():
            ordered = sorted(hours)
            if not ordered:
                continue
            last = hours[ordered[-1]]
            previous = hours[ordered[-2]] if len(ordered) > 1 else 0
            older = hours[ordered[-3]] if len(ordered) > 2 else 0
            velocity = _topic_velocity(last, previous)
            prev_velocity = _topic_velocity(previous, older)
            topics.append(
                TrendingTopic(
                    topic_id=topic_id,
                    topic_name=names[topic_id],
                    velocity=velocity,
                    acceleration=velocity - prev_velocity,
                    sample_size=last,
                )
            )
        topics.sort(key=lambda item: (item.velocity, item.acceleration), reverse=True)
        return TrendingResponse(topics=topics[:limit])
