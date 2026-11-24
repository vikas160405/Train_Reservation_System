
import mysql.connector
import os
from dotenv import load_dotenv

# Load database credentials from .env
load_dotenv()

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        print("MySQL Database Connected Successfully!")
        return connection

    except mysql.connector.Error as error:
        print("Database Connection Error:", error)
        return None
