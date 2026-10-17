#testing
#work in progress stuff
from contextlib import contextmanager
from datetime import datetime, timezone

import mysql.connector
from flask import Blueprint, current_app, jsonify, request

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_TEXT_LENGTH = 100          # matches VARCHAR(100) in seed.sql
MAX_CAPACITY = 1_000_000
UPDATABLE_FIELDS = {"title", "location", "start_datetime", "capacity"}
ER_ROW_IS_REFERENCED = 1451    # MySQL error: a foreign key (ON DELETE RESTRICT) blocked the delete
