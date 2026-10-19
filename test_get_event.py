import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app import app

@pytest.fixture
def client():
  app.config["TESTING"] = True
  with app.test+client() as client:
    yield client

def test_get_event_success(client):
  """Test retrieving an existing event by its ID."""
  
  with patch("app.get_db") as mock_get_db:
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_get_db.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = {
      "event_id": 1,
      "title": "Pottery Workshop",
      "location": "Art Studio",
      "start_datetime": datetime(2026, 11, 1, 14, 0),
      "capacity": 10,
      "registered_count": 2
    }

    response = client.get("/api/vi/events/1")
    data = response.get_json()

    assert response.status_code == 200
    assert data["event_id"] == 1
    assert data["title"] == "Pottery Workshop"
    assert data["capacity"] == 10
    assert data["spots_remaining"] == 8
    
