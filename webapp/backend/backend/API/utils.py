import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
from decimal import Decimal
import json


class DatabaseConnection:
    def __init__(self):
        self.host = 'data.cjgsuu0i0kma.us-east-2.rds.amazonaws.com'
        self.database = 'datadb'
        self.user = 'root'
        self.password = 'UtthamSingh123'
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                port=3306,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("Connection to the database was successful.")
        except Error as error:
            print(f"Error: {error}")
            self.connection = None
            self.cursor = None

    def close(self):
        if self.cursor is not None:
            self.cursor.close()
            print("Cursor closed.")
        if self.connection is not None:
            self.connection.close()
            print("Database connection closed.")

    def __enter__(self):
        return self.connection, self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()



def serialize_data(obj):
    """Helper function to serialize unsupported data types for JSON."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    raise TypeError("Type not serializable")


def create_response(status_code, body):
    """
    Create a standardized API Gateway response with CORS headers.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Allow all origins
            "Access-Control-Allow-Headers": "Content-Type, Authorization",  # Allowed headers
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST",  # Allowed methods
        },
        "body": json.dumps(body),
    }
