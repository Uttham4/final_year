from flask import Blueprint, request, jsonify
import jwt
import bcrypt
from utils import DatabaseConnection, create_response
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

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
        return {
            "validated": is_valid,
            "is_admin": is_admin if is_valid else False
        }
    except Exception as e:
        print(f"Password validation error: {e}")
        return {"validated": False}

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        body = request.get_json()
        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        result = validate_credentials(username, password)
        if result["validated"]:
            token = jwt.encode({
                "username": username,
                "exp": datetime.utcnow() + timedelta(hours=1)
            }, SECRET_KEY, algorithm="HS256")

            return jsonify({
                "message": "Login successful",
                "token": token,
                "admin": result["is_admin"]
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500
