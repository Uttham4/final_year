import json
import jwt
import bcrypt
from utils import *
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"

def validate_credentials(username, password):
    with DatabaseConnection() as (conn, cursor):
        query = "SELECT password, admin FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
    
    if not result:
        return {"validated": False}

    stored_password = result['password']
    is_admin = result['admin']

    try:
        is_valid = bcrypt.checkpw(
            password.encode('utf-8'),
            stored_password.encode('utf-8')
        )
        print({
            "validated": is_valid,
            "is_admin": is_admin if is_valid else False
        })
        return {
            "validated": is_valid,
            "is_admin": is_admin if is_valid else False
        }
    except Exception as e:
        print(f"Password validation error: {e}")
        return {"validated": False}




def login(event, context):
    try:
        body = json.loads(event['body'])
        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            raise ValueError("Username and password are required")

        result = validate_credentials(username, password)
        if result["validated"]:
            token = jwt.encode({
                "username": username,
                "exp": datetime.utcnow() + timedelta(hours=1)
            }, SECRET_KEY, algorithm="HS256")
            return create_response(200, {
                "message": "Login successful",
                "token": token,
                "admin": result["is_admin"]
            })
        else:
            return create_response(401, {"error": "Invalid credentials"})

    except Exception as e:
        print(f"Error: {e}")
        return create_response(500, {"error": "Internal server error"})
