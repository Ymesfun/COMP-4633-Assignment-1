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

@pytest.fixture()
def mocked_database():
    """This fixture generates a mocked database for any tests that need to test if they can successfully post/patch/get/delete from a database."""
    with patch("app.get_db") as mock_get_db:

        mock_connection = MagicMock()

        mock_cursor = MagicMock()



        mock_get_db.return_value = mock_connection

        mock_connection.cursor.return_value = mock_cursor



        yield mock_get_db, mock_connection, mock_cursor


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

#Parametrized test cases with a specified json payload, an expected status code, and an expected error to be returned
@pytest.mark.parametrize("payload, expected_status, expected_error", [
    ({"age": 20}, 400, "No valid fields provided to update"),
    ({"title": ""}, 400, "Title cannot be empty text"),
    ({"location": "   "}, 400, "Location cannot be empty text"),
    ({"capacity": -5}, 400, "Valid positive capacity required"),
    ({"capacity": "ten"}, 400, "Valid positive capacity required"),
    ({"start_datetime": "2020-01-01 10:00:00"}, 400, "New start time must be in the future"),
    ({"start_datetime": "invalid-date-string"}, 400, "Invalid date format. Use YYYY-MM-DD HH:MM:SS"),
])
def test_update_event_validation_errors(client, payload, expected_status, expected_error):
    """Tests if update throws the correct exception on an invalid update request, before any db connections are attempted."""
    response = client.patch("/api/v1/events/1", json=payload)
    data = response.get_json()
    
    assert response.status_code == expected_status
    assert data["error"] == expected_error

def test_update_event_capacity_boundary_conflict(mocked_database, client):
    """Tests if a 409 error is correctly thrown when we try to lower our registrations below our registration count"""
    mock_get_db, mock_connection, mock_cursor = mocked_database
    
    # Quickest way to make it so we have 5 registerred 
    mock_cursor.fetchone.return_value = {'reg_count': 5}
    
    # Attempting to drop capacity to 4 (below registration count)
    response = client.patch("/api/v1/events/1", json={"capacity": 4})
    assert response.status_code == 409

def test_update_event_capacity_boundary_success(mocked_database, client):
    """Tests if the exact boundary value works (e.g. registrations at 5, set to 5)"""
    mock_get_db, mock_connection, mock_cursor = mocked_database
    
    # Need to simulate 5 registrations for this test
    mock_cursor.fetchone.return_value = {'reg_count': 5}
    
    # Boundary value should be good (5 is not less than 5, pass the test!)
    response = client.patch("/api/v1/events/1", json={"capacity": 5})
    assert response.status_code == 200