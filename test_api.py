import pytest
from unittest.mock import patch, MagicMock
from app import app
from datetime import datetime, timedelta

@pytest.fixture
def client():
    """This fixture generates a Flask test client for pytest tests."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get("/api")
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["message"] == "API is running"