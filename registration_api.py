from flask import Blueprint, request, jsonify
from datetime import datetime
from db import get_db
import mysql.connector

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

@registrations_bp.get("/")
def get_registrations():
    """Tries to get a registration associated with a specific event id. This assumes that it will be passed as a query string, e.g.
    a request structured like GET /api/v1/registrations/?event_id=1"""
    # request.args.get gets the query string parameter if its provided (assuming its 'event_id', structured as, ?event_id=1)
    event_id = request.args.get('event_id')
    
    if not event_id: #if we dont use a query string/query param, raise a 400 error
        return jsonify({"error": "event_id query parameter is required"}), 400
        
    if not event_id.isdigit(): #Check if the type is valid for our error case
        return jsonify({"error": "event_id must be a valid integer"}), 400

    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT event_id FROM events WHERE event_id = %s", (event_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Event not found"}), 404 #if event doesnt exist in db, raise a 404 error

        query = """
            SELECT r.registration_id, r.participant_id, p.name
            FROM registrations r
            JOIN participants p ON r.participant_id = p.participant_id
            WHERE r.event_id = %s
        """
        cursor.execute(query, (event_id,))
        registrations = cursor.fetchall()

        return jsonify(registrations), 200

    except mysql.connector.Error:
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()