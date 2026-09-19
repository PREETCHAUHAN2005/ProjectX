import os

os.environ["APP_ENV"] = "test"
os.environ["DEMO_MODE"] = "false"
os.environ["MONGODB_URI"] = ""
os.environ["NEO4J_URI"] = ""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.demo_seed import reset_demo_seed_state
from app.services.ingest import reset_ingest_emit_state
from app.services.live import reset_runtime_for_tests
from app.stores.graph import reset_graph_store_for_tests
from app.stores.posts import reset_post_store_for_tests
from app.ws.gateway import hub


@pytest.fixture(autouse=True)
def reset_runtime_state() -> None:
    reset_post_store_for_tests()
    reset_graph_store_for_tests()
    reset_runtime_for_tests()
    reset_demo_seed_state()
    reset_ingest_emit_state()
    hub.reset_for_tests()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
