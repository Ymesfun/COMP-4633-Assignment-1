import pytest
from unittest.mock import patch, MagicMock
from app import app
from datetime import datetime
import mysql.connector

@pytest.fixture
def client():
    # Provide the Flask test client to all tests
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture()
def mocked_database():
    with patch("app.get_db") as mock_get_db:

        mock_connection = MagicMock()

        mock_cursor = MagicMock()



        mock_get_db.return_value = mock_connection

        mock_connection.cursor.return_value = mock_cursor



        yield mock_get_db, mock_connection, mock_cursor



def test_health(client):
    response = client.get("/api")
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["message"] == "API is running"


def test_create_event_success(mocked_database, client):

    mock_get_db, mock_connection, mock_cursor = mocked_database
    mock_cursor.lastrowid = 1

    payload = {
        "title": "Pottery Class",
        "location": "Art Studio",
        "start_datetime": "2026-11-01 14:00:00",
        "capacity": 20
    }
    
    response = client.post("/api/v1/events", json=payload)
    data = response.get_json()
    
    assert response.status_code == 201
    assert data["event_id"] == 1
    assert data["message"] == "Event created"
    # Check that the mock db was called once.
    mock_cursor.execute.assert_called_once()

def test_create_event_invalid_capacity(client):
    """Test case where the test gives an invalid capacity. Should be rejected before hitting the database."""
    payload = {
        "title": "Pottery Class",
        "location": "Art Studio",
        "start_datetime": "2026-11-01 14:00:00",
        "capacity": -5  # Invalid capacity
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 400



def test_list_events_success(mocked_database, client):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    #test data 
    mock_cursor.fetchall.return_value = [
    {"event_id": 1, "title": "Pottery Workshop", "location": "Art Studio",
    "start_datetime": datetime(2026, 11, 1, 14, 0, 0),
    "capacity": 10, "registered_count": 2},
    {"event_id": 2, "title": "Board Game Night", "location": "Wyckham House",
    "start_datetime": datetime(2026, 11, 5, 18, 0, 0),
    "capacity": 20, "registered_count": 0},
    ]


    response = client.get("/api/v1/events")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["start_datetime"] == "2026-11-01 14:00:00"
    assert data[0]["spots_remaining"] == 8
    assert data[1]["spots_remaining"] == 20

def test_list_events_database_error(mocked_database, client):
    mock_get_db, mock_connection, mock_cursor = mocked_database
    mock_cursor.execute.side_effect = mysql.connector.Error("FAIL")

    response = client.get("/api/v1/events")

    assert response.status_code == 500
    assert response.get_json() == {"error": "database error detected"}