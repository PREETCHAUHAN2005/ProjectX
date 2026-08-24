from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_timeline_empty() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/analytics/timeline")
    assert response.status_code == 200
    body = response.json()
    assert body == {"buckets": []}


def test_network_graph_empty() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/analytics/network-graph")
    assert response.status_code == 200
    assert response.json() == {"nodes": [], "links": []}


def test_demographics_empty() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/analytics/demographics")
    assert response.status_code == 200
    assert response.json() == {"country": [], "language": [], "profession": []}


def test_trending_empty() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/topics/trending")
    assert response.status_code == 200
    assert response.json() == {"topics": []}


def test_trending_rejects_invalid_limit() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/topics/trending", params={"limit": 0})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid request"}
