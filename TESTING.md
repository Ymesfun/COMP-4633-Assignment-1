# Campus Events Booking API - Testing Documentation

## 1. Testing Overview

The Campus Events Booking API uses pytest to test its REST API endpoints.

Our automated tests use Flask's test client to simulate HTTP requests and verify that th e API returns the expected responses.

We also use unittest.mock to simulate database connections and operations. This allows us to test API functionality without requiring a live MySQL database.

## 2. Current Test Results

- Testing framework: pytest
- Programming language: Python
- Test execution: GitHub
- Total tests: 42
- Passed: 42
- Failed: 0

The automated tests cover successful requests, invalid inputs, business-rule violations, and database error handling.

These results represent mocked tests and do not independently verify integration with a live MySQL database.
