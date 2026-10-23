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

| Assignment Requirements | Test Names |
|---|---|
| Create an event | `test_create_event_success`, `test_create_event_invalid_capacity` |
| List all events | `test_list_events_success`, `test_list_events_database_error` |
| Retrieve a single event | `test_get_event_success`, `test_get_event_not_found`, `test_get_event_database_error` |
| Update an event | `test_update_event_validation_errors`, `test_update_event_capacity_boundary_conflict`, `test_update_event_capacity_boundary_success` |
| Delete an event | `test_delete_event_logic_errors`, `test_delete_event_success`, `test_delete_event_database_error` |
| Register a participant | `test_register_missing_fields`, `test_register_event_not_found`, `test_register_event_started_boundary`, `test_register_event_at_capacity`, `test_register_success`, `test_register_integrity_errors` |
| Cancel a registration | `test_cancel_registration_success`, `test_cancel_registration_not_found`, `test_cancel_registration_database_error` |
| List registrations | `test_get_registrations_missing_query_param`, `test_get_registrations_invalid_query_param`, `test_get_registrations_event_not_found`, `test_get_registrations_success`, `test_get_registrations_empty_success`, `test_get_registrations_database_error` |

### Single Event Retrieval Tests

The following three tests were added to 'test_get_event.py':

1. 'test_get_event_success'
   - Verifies that an existing event can be retreieved.
   - Checks the HTTP 200 response and returned event details.
  
2. 'test_get_event_not_found'
   - Verifies that requesting a nonexistent event returns HTTP 404.

3. 'test_get_event_database_error'
   - Verifies that a database error produces HTTP 500.
