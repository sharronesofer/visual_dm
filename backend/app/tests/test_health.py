from fastapi.testclient import TestClient
import pytest

from backend.app.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_health_endpoint(client):
    """Test that the health endpoint returns a success response."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "version" in response.json()


def test_api_root_redirect(client):
    """Test that the root endpoint redirects to docs."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/docs"


def test_api_health_endpoint(client):
    """Test that the API health endpoint returns a success response."""
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert "version" in response.json()
    assert response.json()["status"] == "healthy" 