import os
from flask import Flask, jsonify, request
import mysql.connector
from dotenv import load_dotenv

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


