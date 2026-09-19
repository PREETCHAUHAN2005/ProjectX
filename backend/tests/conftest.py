import os

os.environ["APP_ENV"] = "test"
os.environ["DEMO_MODE"] = "false"
os.environ["MONGODB_URI"] = ""
os.environ["NEO4J_URI"] = ""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.live import reset_runtime_for_tests
from app.stores.graph import reset_graph_store_for_tests
from app.stores.posts import reset_post_store_for_tests
from app.ws.gateway import hub


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    reset_post_store_for_tests()
    reset_graph_store_for_tests()
    reset_runtime_for_tests()
    hub.reset_for_tests()
    with TestClient(app) as test_client:
        yield test_client
