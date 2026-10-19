#testing
#work in progress stuff
from contextlib import contextmanager
from datetime import datetime, timezone

import mysql.connector
from flask import Blueprint, current_app, jsonify, request

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_TEXT_LENGTH = 100          # VARCHAR(100) in seed.sql
MAX_CAPACITY = 1_000_000
UPDATABLE_FIELDS = {"title", "location", "start_datetime", "capacity"}
ER_ROW_IS_REFERENCED = 1451    # MySQL error: a foreign key (ON DELETE RESTRICT) blocked the delete



# registered_count is computed from the registrations table every time, never stored.
EVENT_SELECT = """
    SELECT e.event_id, e.title, e.location, e.start_datetime, e.capacity,
           (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.event_id) AS registered_count
    FROM events e
"""


class ApiError(Exception):
    """An error we want to send to the client as {"error": message} with this HTTP status."""

    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)



#this seems off need to rethink this 

def event_to_json(row):
    return {
        "event_id": row["event_id"],
        "title": row["title"],
        "location": row["location"],
        "start_datetime": row["start_datetime"].strftime(DATETIME_FORMAT),
        "capacity": row["capacity"],
        "registered_count": row["registered_count"],
        "spots_remaining": row["capacity"] - row["registered_count"],
    }


def parse_start_datetime(value):
    """Turn "YYYY-MM-DD HH:MM:SS" into a datetime, or raise a 400 ApiError."""
    if not isinstance(value, str):
        raise ApiError(400, "start_datetime must be a string in the format YYYY-MM-DD HH:MM:SS")
    try:
        return datetime.strptime(value, DATETIME_FORMAT)
    except ValueError:
        raise ApiError(400, "start_datetime must be a valid date in the format YYYY-MM-DD HH:MM:SS")



def validate_update(data):
    """Check the body of a PATCH request. Returns only the fields to change, cleaned up."""
    if not isinstance(data, dict):
        raise ApiError(400, "Request body must be a JSON object")
    unknown = sorted(set(data) - UPDATABLE_FIELDS)
    if unknown:
        raise ApiError(400, "Unknown field(s): " + ", ".join(unknown))
    if not data:
        raise ApiError(400, "Provide at least one field to update: " + ", ".join(sorted(UPDATABLE_FIELDS)))

    clean = {}
    for field in ("title", "location"):
        if field in data:
            value = data[field]
            if not isinstance(value, str) or not value.strip():
                raise ApiError(400, f"{field} must be a non-empty string")
            if len(value.strip()) > MAX_TEXT_LENGTH:
                raise ApiError(400, f"{field} must be at most {MAX_TEXT_LENGTH} characters")
            clean[field] = value.strip()

    if "capacity" in data:
        value = data["capacity"]
        # bool is not a number 
        if isinstance(value, bool) or not isinstance(value, int):
            raise ApiError(400, "capacity must be an integer")
        if value <= 0:
            raise ApiError(400, "Capacity must be positive")
        if value > MAX_CAPACITY:
            raise ApiError(400, f"capacity must be at most {MAX_CAPACITY}")
        clean["capacity"] = value

    if "start_datetime" in data:
        clean["start_datetime"] = parse_start_datetime(data["start_datetime"])
    return clean


def create_events_blueprint(get_db):
    """get_db is passed in (instead of imported) so this file never has to import app.py"""
    bp = Blueprint("events", __name__)

    @contextmanager
    def transaction():
        """Open a connection and dict cursor. Commit if the block works, roll back if it fails"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()


    def fetch_event(cursor, event_id, lock=False):
        # lock=True adds FOR UPDATE: other requests wait until commit, so
        # registration count we read stays accurate while we decide.
        cursor.execute(
            EVENT_SELECT + " WHERE e.event_id = %s" + (" FOR UPDATE" if lock else ""),
            (event_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise ApiError(404, "Event not found")
        return row

    @bp.errorhandler(ApiError)
    def handle_api_error(err):
        return jsonify({"error": err.message}), err.status

    @bp.errorhandler(mysql.connector.Error)
    def handle_db_error(err):
        # Details go to the server log only, never to the client.
        current_app.logger.error("Database error: %s", err)
        return jsonify({"error": "Database error occurred"}), 500




 # ---------------------------------------------------------------- list events
    @bp.get("/api/v1/events")
    def list_events():
        with transaction() as cursor:
            cursor.execute(EVENT_SELECT + " ORDER BY e.start_datetime, e.event_id")
            rows = cursor.fetchall()
        return jsonify({"count": len(rows), "events": [event_to_json(r) for r in rows]}), 200

    # ---------------------------------------------------------------- get one event
    @bp.get("/api/v1/events/<int:event_id>")
    def get_event(event_id):
        with transaction() as cursor:
            event = event_to_json(fetch_event(cursor, event_id))
        return jsonify(event), 200

