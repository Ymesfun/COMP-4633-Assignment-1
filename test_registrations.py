import pytest
import mysql.connector
from unittest.mock import patch, MagicMock
from app import app  
from datetime import datetime

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture()
def mocked_database():
    with patch("registration_api.get_db") as mock_get_db: 
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        yield mock_get_db, mock_connection, mock_cursor

def test_register_missing_fields(client):
    """Test 400 error when payload is missing required IDs."""
    response = client.post("/api/v1/registrations/", json={"event_id": 1})
    assert response.status_code == 400
    assert response.get_json()["error"] == "event_id and participant_id are required"

def test_register_event_not_found(mocked_database, client):
    """Test 404 error when the event does not exist."""
    _, _, mock_cursor = mocked_database
    mock_cursor.fetchone.return_value = None  # Simulate no event found
    
    response = client.post("/api/v1/registrations/", json={"event_id": 999, "participant_id": 1})
    assert response.status_code == 404

def test_register_event_started_boundary(mocked_database, client):
    """Test boundary where the event starts exactly right now (should fail)."""
    _, _, mock_cursor = mocked_database
    
    # Event start time is exactly now
    mock_cursor.fetchone.return_value = {
        'capacity': 10, 
        'current_regs': 5, 
        'start_datetime': datetime.now() 
    }
    
    response = client.post("/api/v1/registrations/", json={"event_id": 1, "participant_id": 1})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Cannot register for an event that has already started"

def test_register_event_at_capacity(mocked_database, client):
    """Test boundary where current registrations exactly equal capacity."""
    _, _, mock_cursor = mocked_database
    
    # Event is full (10 registrations) and happens in the future
    future_date = datetime.now().replace(year=2030)
    mock_cursor.fetchone.return_value = {
        'capacity': 10, 
        'current_regs': 10, 
        'start_datetime': future_date
    }
    
    response = client.post("/api/v1/registrations/", json={"event_id": 1, "participant_id": 1})
    assert response.status_code == 409
    assert response.get_json()["error"] == "Event is at full capacity"

def test_register_success(mocked_database, client):
    """Test a successful registration."""
    _, _, mock_cursor = mocked_database
    
    future_date = datetime.now().replace(year=2030)
    mock_cursor.fetchone.return_value = {
        'capacity': 10, 
        'current_regs': 5, 
        'start_datetime': future_date
    }
    mock_cursor.lastrowid = 42
    
    response = client.post("/api/v1/registrations/", json={"event_id": 1, "participant_id": 1})
    data = response.get_json()
    
    assert response.status_code == 201
    assert data["message"] == "Successfully registered"
    assert data["registration_id"] == 42
    mock_cursor.execute.assert_called() # Verify that the SQL was actually called/executed

#Parametrized test to check the two exception cases (duplicate entries, missing participant)
@pytest.mark.parametrize("error_message, expected_status, expected_response", [
    ("duplicate entry '1-1' for key", 409, "Participant is already registered for this event"),
    ("foreign key constraint fails ... participant_id", 404, "Participant not found"),
])
def test_register_integrity_errors(mocked_database, client, error_message, expected_status, expected_response):
    """Test database constraint violations translating to proper HTTP errors."""
    _, _, mock_cursor = mocked_database
    
    future_date = datetime.now().replace(year=2030)
    mock_cursor.fetchone.return_value = {
        'capacity': 10, 
        'current_regs': 5, 
        'start_datetime': future_date
    }
    
    # The first execute() is the SELECT (handled by fetchone mock), the second is the INSERT
    # We need to apply a side effect to trigger the IntegrityError on the INSERT
    mock_cursor.execute.side_effect = [None, mysql.connector.IntegrityError(error_message)]
    
    response = client.post("/api/v1/registrations/", json={"event_id": 1, "participant_id": 1})
    assert response.status_code == expected_status
    assert response.get_json()["error"] == expected_response

def test_cancel_registration_success(mocked_database, client):
    """Test successful deletion of a registration."""
    _, mock_connection, mock_cursor = mocked_database
    
    # Simulate exactly 1 row being deleted
    mock_cursor.rowcount = 1
    
    response = client.delete("/api/v1/registrations/1")
    data = response.get_json()
    
    assert response.status_code == 200
    assert data["message"] == "Registration successfully cancelled"
    
    # Verify the correct SQL was executed and committed
    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()

def test_cancel_registration_not_found(mocked_database, client):
    """Test 404 error when attempting to delete a registration ID that doesn't exist."""
    _, _, mock_cursor = mocked_database
    
    # Simulate no rows matching the WHERE clause
    mock_cursor.rowcount = 0
    
    response = client.delete("/api/v1/registrations/999")
    data = response.get_json()
    
    assert response.status_code == 404
    assert data["error"] == "Registration not found"

def test_cancel_registration_database_error(mocked_database, client):
    """Test 500 error when the database throws an exception."""
    _, _, mock_cursor = mocked_database
    
    # Simulate a database crash during the execution
    mock_cursor.execute.side_effect = mysql.connector.Error("Connection lost")
    
    response = client.delete("/api/v1/registrations/1")
    data = response.get_json()
    
    assert response.status_code == 500
    assert data["error"] == "Database error occurred"

def test_get_registrations_missing_query_param(client):
    """Test 400 error when ?event_id= is missing."""
    response = client.get("/api/v1/registrations/")
    data = response.get_json()
    
    assert response.status_code == 400
    assert data["error"] == "event_id query parameter is required"

def test_get_registrations_invalid_query_param(client):
    """Test 400 error when ?event_id= is not an integer."""
    response = client.get("/api/v1/registrations/?event_id=abc")
    data = response.get_json()
    
    assert response.status_code == 400
    assert data["error"] == "event_id must be a valid integer"

def test_get_registrations_event_not_found(mocked_database, client):
    """Test 404 error when the event does not exist in the database."""
    _, _, mock_cursor = mocked_database
    
    # Simulate the first query (SELECT event_id) returning None
    mock_cursor.fetchone.return_value = None
    
    response = client.get("/api/v1/registrations/?event_id=999")
    data = response.get_json()
    
    assert response.status_code == 404
    assert data["error"] == "Event not found"

def test_get_registrations_success(mocked_database, client):
    """Test 200 success returning a list of registrations."""
    _, _, mock_cursor = mocked_database
    
    # Simulate the first query (event exists)
    mock_cursor.fetchone.return_value = {"event_id": 1}
    
    # Simulate the second query (returning joined registration data)
    mock_cursor.fetchall.return_value = [
        {"registration_id": 1, "participant_id": 101, "first_name": "John", "last_name": "Doe"},
        {"registration_id": 2, "participant_id": 102, "first_name": "Jane", "last_name": "Smith"}
    ]
    
    response = client.get("/api/v1/registrations/?event_id=1")
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["first_name"] == "John"
    assert data[1]["participant_id"] == 102

def test_get_registrations_empty_success(mocked_database, client):
    """Test 200 success returning an empty list when event exists but has no registrations."""
    _, _, mock_cursor = mocked_database
    
    # Simulate that an event with id 1 exists 
    mock_cursor.fetchone.return_value = {"event_id": 1}
    
    # Simulate no registrations found
    mock_cursor.fetchall.return_value = []
    
    response = client.get("/api/v1/registrations/?event_id=1")
    data = response.get_json()
    
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_registrations_database_error(mocked_database, client):
    """Test 500 error on database crash."""
    _, _, mock_cursor = mocked_database
    
    # Simulate a database failure on execution
    mock_cursor.execute.side_effect = mysql.connector.Error("Connection lost")
    
    response = client.get("/api/v1/registrations/?event_id=1")
    data = response.get_json()
    
    assert response.status_code == 500
    assert data["error"] == "Database error occurred"