import os
import mysql.connector

def get_db():
    """This function opens a connection to the mysql database using environment variables."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "campus_events"),
        port=os.getenv("MYSQL_PORT", 3306)
    )