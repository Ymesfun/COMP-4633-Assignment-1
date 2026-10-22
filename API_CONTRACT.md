# API commands
| Operation | Method & Path | Params | Request Body | Success Response | Error Response |
| --- | --- | --- | --- | --- | --- |
| Health Check | /api | None | "status : ok" "message : api is running" | None | None |
| Create Event | POST `/api/v1/events` | None | `{"title": "Art Viewing ", "location": "Room", "start_datetime": "2026-11-01 14:00:00", "capacity": 20}` | 201 Created `{"message": "Event created", "event_id": 1}` | 400 Missing fields/Invalid capacity, 500 Database error|
| Update Event | `PATCH /api/v1/events/<int:event_id>` | Path Parameter: `event_id` | Send a valid field, e.g. `{"capacity": 30}` | 200 OK `{"message": "Event successfully updated"}` | 400 Invalid data, 404 Event not found, 409 Capacity conflict, 500 DB Error |
| List Events | GET `/api/v1/events` | None | None | 200 OK `[{"event_id": 1, "title": "Art Viewing", "spots_remaining": 5...}]` |   500 Database error |
| Get Event | GET `/api/v1/events/<int:event_id>` | Path Parameter: `event_id` | None | 200 OK `{"event_id": 1, "title": "Art", "spots_remaining": 5...}` | 404 Event not found, 500 Database error |
| Delete Event | DELETE `/api/v1/events/<int:event_id>` | Path Parameter: `event_id` | None | 200 OK `{"message": "Event successfully deleted"}` | 404 Event not found, 409 Active registrations, 500 DB Error |
| Register Participant | POST `/api/v1/registrations/` | None | `{"event_id": 1, "participant_id": 4}` | 201 Created `{"message": "Successfully registered", "registration_id": 1}` | 400 Invalid input, 404 Event/Participant not found, 409 Full capacity/Duplicate, 500 DB Error |
| Cancel Registration | DELETE `/api/v1/registrations/<int:registration_id>`|  Path Parameter: `registration_id`| None | 200 OK `{"message": "Registration successfully cancelled"}` | 404 Registration not found, 500 Database error |
| Get Registrations | GET `/api/v1/registrations/` |Query Parameter: `?event_id=1` | None | 200 OK `[{"registration_id": 1, "participant_id": 4, "name": "John"}]` |   400 Missing/invalid param, 404 Event not found, 500 Database error |