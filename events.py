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
