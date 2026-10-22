# Campus Events Booking API - Testing Documentation

## 1. Testing Overview

The Campus Events Booking API uses pytest to test its REST API endpoints.

Our automated tests use Flask's test client to simulate HTTP requests and verify that th e API returns the expected responses.

We also use unittest.mock to simulate database connections and operations. This allows us to test API functionality without requiring a live MySQL database.

## 2. Current Test Results

- Testing framework: pytest
- Programming language: Python
- Test execution: GitHub
- Total tests: 48
- Passed: 48
- Failed: 0

The automated tests cover successful requests, invalid inputs, business-rule violations, and database error handling.

These results represent mocked tests and do not independently verify integration with a live MySQL database.

## 3. Test Coverage Mapping

The following table identifies the automated test files associated with the API requirements.

| Assignment Requirements | Test File | Status |
|---|---|---|
| Create an event | test_api.py / test_events_api.py | Tests implemented |
| List all events | test_api.py / test_events_api.py | Tests implemented |
| Retrieve a single event | test_get_event.py | Tests implemented |
| Update an event | test_api.py / test_events_api.py | Tests implemented |
| Delete an event | test_api.py / test_events_api.py | Tests implemented |
| Register a participant | test_registrations.py | Tests implemented |
| Cancel a registration | test_registrations.py | Tests implemented |
| List registrations with participant names | test_registrations.py | Tests Implemented |

### Single Event Retrieval Tests

The following three tests were added to 'test_get_event.py':

1. 'test_get_event_success'
   - Verifies that an existing event can be retreieved.
   - Checks the HTTP 200 response and returned event details.
  
2. 'test_get_event_not_found'
   - Verifies that requesting a nonexistent event returns HTTP 404.

3. 'test_get_event_database_error'
   - Verifies that a database error produces HTTP 500.
