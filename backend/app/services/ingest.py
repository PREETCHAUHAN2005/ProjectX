from typing import Any

from app.stores.graph import get_graph_store
from app.stores.posts import get_post_store


def persist_analyzed_post(document: dict[str, Any]) -> None:
    get_post_store().upsert(document)
    get_graph_store().ingest_post(document)
