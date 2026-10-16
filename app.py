import os
from flask import Flask, jsonify, request
import mysql.connector
from dotenv import load_dotenv

#Fetches environment vars from .env file
load_dotenv()

app = Flask(__name__)


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