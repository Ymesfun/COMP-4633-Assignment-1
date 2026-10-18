import os
from flask import Flask, jsonify, request
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime

#Fetches environment vars from .env file
load_dotenv()

app = Flask(__name__)
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_TEXT_LENGHT = 100

def get_db():
    """This function opens a connection to the mysql database using environment variables."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "campus_events"),
        port=os.getenv("MYSQL_PORT", 3306)
    )

@app.get("/api")
def health():
    """Basic health check api call."""
    return jsonify({"status": "ok", "message": "API is running"}), 200

@app.post("/api/v1/events")
def create_event():
    """This function is an API call to the database to make a post request to create a new event in our events table"""
    data = request.get_json()
    #If the data is not appropriately formatted, we should raise a 400 bad request error
    required_fields = ['title', 'location', 'start_datetime', 'capacity']
    if not all(field in data for field in required_fields): 
        return jsonify({"error": "Missing required fields"}), 400
        
    if int(data['capacity']) <= 0:
        return jsonify({"error": "Capacity must be positive"}), 400

    query = """
        INSERT INTO events (title, location, start_datetime, capacity)
        VALUES (%s, %s, %s, %s)
    """ # Parametried query to insert a new event into our table safely.
    values = (data['title'], data['location'], data['start_datetime'], data['capacity'])
    #Initialize to none to tell whether or not we need to clean them up after we finish up with the try/except block
    conn = None
    cursor = None
    try: #Try to see if we can actually connect to the DB and send our request
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        event_id = cursor.lastrowid
        return jsonify({"message": "Event created", "event_id": event_id}), 201
    except mysql.connector.Error as err: #Raise an exception, 500 errors are internal errors (e.g., db)
        return jsonify({"error": "Database error occurred"}), 500
    finally: #Close our connection after we're done to prevent any leaking.
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.patch("/api/v1/events/<int:event_id>")
def update_event_details(event_id):
    body = request.get_json(silent=True) or {}
    if not body:
        return jsonify({"error": "No Valid data provided in body to update"}), 400
    new_capacity = body.get('capacity')
    update_information = []
    values = []

    # Need to validate every field that exists, why we need to search through our json body and validate if inputs are invalid
    if 'title' in body:
        title = body['title']
        if not title or not str(title).strip():
            return jsonify({"error": "Title cannot be empty text"}), 400
        update_information.append("title = %s")
        values.append(str(title).strip())

    if 'location' in body:
        location = body['location']
        if not location or not str(location).strip():
            return jsonify({"error": "Location cannot be empty text"}), 400
        update_information.append("location = %s")
        values.append(str(location).strip())

    if 'start_datetime' in body:
        start_datetime_str = body['start_datetime']
        try:
            new_time = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
            if new_time <= datetime.now():
                return jsonify({"error": "New start time must be in the future"}), 400
            
            update_information.append("start_datetime = %s")
            values.append(start_datetime_str)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"}), 400

    new_capacity = None
    if 'capacity' in body:
        new_capacity = body['capacity']
        if not isinstance(new_capacity, int) or new_capacity <= 0:
            return jsonify({"error": "Valid positive capacity required"}), 400

    if not update_information and new_capacity is None:
         return jsonify({"error": "No valid fields provided to update"}), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # Need to validate if there is a valid capacity update (can't be zero, cant be lower than existing registrations)
        if new_capacity is not None:
            new_capacity = body['capacity']
            if not isinstance(new_capacity, int) or new_capacity <= 0:
                return jsonify({"error": "Valid positive capacity required"}), 400
            
            cursor.execute("SELECT COUNT(*) as reg_count FROM registrations WHERE event_id = %s", (event_id,))
            result = cursor.fetchone()
            current_registrations = result['reg_count'] if result else 0
            
            if new_capacity < current_registrations: # 409 - conflict with current state of target resource (Cant lower capacity below existing registrations) 
                return jsonify({"error": "Capacity cannot be lower than existing registrations"}), 409
            
            update_information.append("capacity = %s")
            values.append(new_capacity)

        query = f"UPDATE events SET {', '.join(update_information)} WHERE event_id = %s"
        values.append(event_id)

        cursor.execute(query, tuple(values))
        conn.commit()

        if cursor.rowcount == 0: #Guard against modifying a null row
             return jsonify({"error": "Event not found"}), 404

        return jsonify({"message": "Event successfully updated"}), 200
    
    except mysql.connector.Error:
        return jsonify({"error": "Database error occurred"}), 500
    finally: #Close up remaining connections if they are open
        if cursor:
            cursor.close()
        if conn: 
            conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)


#returns a list of all events
@app.get("/api/v1/events")
def list_events():
    query = """ SELECT e.event_id, e.title, e.location, e.start_datetime, e.capacity, 
                    (SELECT COUNT(*) 
                    FROM registractions r 
                    WHERE r.event_id = e.event_id) AS registered_count
                    FROM events e
                ORDER BY e.start_datetime"""

    conn = None
    cursor = None
    try:
        conn = get_db()
        #returns each row as a dict to use title instead of row
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()


        # convert each rw into json accetable data
        events = []
        for row in rows:
            events.append({
                "event_id": row["event_id"],
                "title": row["title"],
                "location": row["location"],
                "start_datetime": row["start_datetime"].strftime(DATETIME_FORMAT),
                "capacity": row["capacity"],
                "registered_count": row["registered_count"],
                "spots_remaining": row["capacity"] - row["registered_count"],
            })
        return jsonify(events), 200
    except mysql.connector.Error:
        return jsonify({"error": "database error detected"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.delete("/api/v1/events/<int:event_id>")
def delete_event(event_id):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # Check if registrations exist
        cursor.execute("SELECT COUNT(*) as reg_count FROM registrations WHERE event_id = %s", (event_id,))
        result = cursor.fetchone()
        
        if result and result['reg_count'] > 0: #Error state - active registrations
            return jsonify({"error": "Cannot delete event with active registrations"}), 409

        cursor.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
        conn.commit()

        if cursor.rowcount == 0: #Check if we havent removed any rows AKA the event doesn't exist
            return jsonify({"error": "Event not found"}), 404

        return jsonify({"message": "Event successfully deleted"}), 200

    except mysql.connector.Error:
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()