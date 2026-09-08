"""Neo4j-shaped graph with an in-memory fallback.

Confirmed: (:User {id, handle, platform}), (:Topic {name}),
(:User)-[:INTERACTED {type, timestamp, weight}]->(:User)

PageRank and community coloring are computed in-process when Neo4j GDS is
not available (implementation, not source-confirmed algorithm names).
"""

from __future__ import annotations

import logging
import re
from typing import Any

from app.core.config import settings
from app.schemas.contracts import GraphLink, GraphNode

logger = logging.getLogger(__name__)

MENTION_RE = re.compile(r"@([A-Za-z0-9_]{1,32})")


def _dominant_emotion(emotions: list[Any]) -> str:
    best_label = ""
    best_score = -1.0
    for item in emotions:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "")
        try:
            score = float(item.get("score") or 0.0)
        except (TypeError, ValueError):
            continue
        if label and score > best_score:
            best_label = label
            best_score = score
    return best_label


class MemoryGraphStore:
    def __init__(self) -> None:
        self.users: dict[str, dict[str, str]] = {}
        self.topics: set[str] = set()
        self.interactions: list[dict[str, Any]] = []
        # IMPLEMENTATION: last dominant emotion per user for readable community colors.
        self.user_community: dict[str, str] = {}

    def upsert_user(self, user_id: str, handle: str, platform: str) -> None:
        self.users[user_id] = {"id": user_id, "handle": handle, "platform": platform}

    def upsert_topic(self, name: str) -> None:
        if name:
            self.topics.add(name)

    def add_interaction(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        timestamp: str,
        weight: float,
    ) -> None:
        self.interactions.append(
            {
                "source": source_id,
                "target": target_id,
                "type": rel_type,
                "timestamp": timestamp,
                "weight": weight,
            }
        )

    def ingest_post(
        self,
        document: dict[str, Any],
        *,
        reply_to_user_id: str | None = None,
    ) -> None:
        author = document.get("author") or {}
        user_id = str(author.get("user_id") or "")
        handle = str(author.get("handle") or "")
        platform = str(document.get("platform") or "")
        if user_id:
            self.upsert_user(user_id, handle, platform)
        analytics = document.get("analytics") or {}
        topic_name = analytics.get("topic_name")
        if isinstance(topic_name, str) and topic_name:
            self.upsert_topic(topic_name)
        dominant = _dominant_emotion(analytics.get("emotions") or [])
        if user_id and dominant:
            self.user_community[user_id] = dominant
        raw_text = str((document.get("content") or {}).get("raw_text") or "")
        timestamp = str(document.get("timestamp") or "")
        if reply_to_user_id and user_id and reply_to_user_id != user_id:
            if reply_to_user_id not in self.users:
                self.upsert_user(reply_to_user_id, reply_to_user_id, platform)
            self.add_interaction(user_id, reply_to_user_id, "reply", timestamp, 1.5)
        for mention in MENTION_RE.findall(raw_text):
            if mention.lower() == handle.lower():
                continue
            existing_id = next(
                (
                    uid
                    for uid, meta in self.users.items()
                    if meta["handle"].lower() == mention.lower()
                ),
                None,
            )
            mention_id = existing_id or f"mention:{mention.lower()}"
            if mention_id not in self.users:
                self.upsert_user(mention_id, mention, platform)
            if mention_id not in self.user_community:
                self.user_community[mention_id] = "neutral"
            self.add_interaction(user_id, mention_id, "mention", timestamp, 1.0)

    def snapshot(
        self,
        *,
        min_centrality: float | None = None,
        min_weight: float | None = None,
    ) -> tuple[list[GraphNode], list[GraphLink]]:
        links = [
            GraphLink(
                source=str(item["source"]),
                target=str(item["target"]),
                type=str(item["type"]),
                timestamp=str(item["timestamp"]),
                weight=float(item["weight"]),
            )
            for item in self.interactions
            if min_weight is None or float(item["weight"]) >= min_weight
        ]
        ranks = _pagerank(list(self.users), links)
        communities = _communities(list(self.users), links)
        nodes: list[GraphNode] = []
        for user_id, meta in self.users.items():
            rank = ranks.get(user_id, 0.0)
            if min_centrality is not None and rank < min_centrality:
                continue
            nodes.append(
                GraphNode(
                    id=user_id,
                    handle=meta["handle"],
                    platform=meta["platform"],
                    pagerank=rank,
                    community=self.user_community.get(
                        user_id, communities.get(user_id, "neutral")
                    ),
                )
            )
        allowed = {node.id for node in nodes}
        links = [
            link for link in links if link.source in allowed and link.target in allowed
        ]
        return nodes, links

    def clear(self) -> None:
        self.users.clear()
        self.topics.clear()
        self.interactions.clear()
        self.user_community.clear()


def _pagerank(user_ids: list[str], links: list[GraphLink], iterations: int = 15) -> dict[str, float]:
    if not user_ids:
        return {}
    n = len(user_ids)
    index = {user_id: i for i, user_id in enumerate(user_ids)}
    rank = [1.0 / n] * n
    outbound: list[list[int]] = [[] for _ in range(n)]
    for link in links:
        if link.source in index and link.target in index:
            outbound[index[link.source]].append(index[link.target])
    damping = 0.85
    for _ in range(iterations):
        nxt = [(1.0 - damping) / n] * n
        for i, outs in enumerate(outbound):
            if not outs:
                share = damping * rank[i] / n
                for j in range(n):
                    nxt[j] += share
            else:
                share = damping * rank[i] / len(outs)
                for j in outs:
                    nxt[j] += share
        rank = nxt
    return {user_ids[i]: rank[i] for i in range(n)}


def _communities(user_ids: list[str], links: list[GraphLink]) -> dict[str, str]:
    parent = {user_id: user_id for user_id in user_ids}

    def find(node: str) -> str:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for link in links:
        if link.source in parent and link.target in parent:
            union(link.source, link.target)
    roots: dict[str, str] = {}
    next_id = 0
    out: dict[str, str] = {}
    for user_id in user_ids:
        root = find(user_id)
        if root not in roots:
            roots[root] = str(next_id)
            next_id += 1
        out[user_id] = roots[root]
    return out


_graph: MemoryGraphStore | None = None


def get_graph_store() -> MemoryGraphStore:
    global _graph
    if _graph is None:
        _graph = MemoryGraphStore()
        if settings.neo4j_uri:
            logger.warning(
                "NEO4J_URI is set but the live Neo4j driver is not wired; "
                "using in-memory graph until the driver is connected"
            )
    return _graph


def reset_graph_store_for_tests() -> MemoryGraphStore:
    global _graph
    _graph = MemoryGraphStore()
    return _graph
