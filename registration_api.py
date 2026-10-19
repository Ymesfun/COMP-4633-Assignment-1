from flask import Blueprint, request, jsonify
import mysql.connector
from datetime import datetime
from db import get_db

registrations_bp = Blueprint('registrations', __name__, url_prefix='/api/v1/registrations')

#Implied path here is POST /api/v1/registrations/
@registrations_bp.post("/")
def register_for_event():
    data = request.get_json(silent=True) or {}
    event_id = data.get('event_id')
    participant_id = data.get('participant_id')

    if not event_id or not participant_id:
        return jsonify({"error": "event_id and participant_id are required"}), 400

    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True) 
        # this is so cursor treats the db conn as a dict instead of tuple (makes accessing db values easier)

        check_query = """
            SELECT e.capacity, e.start_datetime, 
                   (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.event_id) as current_regs
            FROM events e
            WHERE e.event_id = %s
        """
        cursor.execute(check_query, (event_id,))
        event = cursor.fetchone()

        if not event:
            return jsonify({"error": "Event not found"}), 404 # Raise an error if the event does not exist

        if event['start_datetime'] <= datetime.now(): # Raise an error if the event has alreaday passed
            return jsonify({"error": "Cannot register for an event that has already started"}), 400

        if event['current_regs'] >= event['capacity']: # Raisie an error if capacity is over limit
            return jsonify({"error": "Event is at full capacity"}), 409
        
        # If there are no issues, insert the registration into our registrations
        insert_query = "INSERT INTO registrations (event_id, participant_id) VALUES (%s, %s)"
        cursor.execute(insert_query, (event_id, participant_id))
        conn.commit()

        return jsonify({
            "message": "Successfully registered", 
            "registration_id": cursor.lastrowid
        }), 201

    except mysql.connector.IntegrityError as err:
        # Try and catch any DB integrity errors caused by duplicate registrations and invalid participant IDs based on sql table constraints
        error_msg = str(err).lower()
        if "duplicate entry" in error_msg:
            return jsonify({"error": "Participant is already registered for this event"}), 409
        elif "foreign key constraint fails" in error_msg and "participant_id" in error_msg:
            return jsonify({"error": "Participant not found"}), 404
        return jsonify({"error": "Database integrity error"}), 400
    except mysql.connector.Error:
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@registrations_bp.delete("/<int:registration_id>")
def cancel_registration(registration_id):
    """This simply tries to delete a registration, and returns a status code based on if the registration exists and was successfully deleted."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Try to delete the given registration id
        cursor.execute("DELETE FROM registrations WHERE registration_id = %s", (registration_id,))
        conn.commit()

        # If rowcount is 0, then the registration_id didn't actually exist
        if cursor.rowcount == 0:
            return jsonify({"error": "Registration not found"}), 404

        return jsonify({"message": "Registration successfully cancelled"}), 200

    except mysql.connector.Error:
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()