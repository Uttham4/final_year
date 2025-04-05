from flask import Blueprint, request, jsonify
import bcrypt
from utils import DatabaseConnection
from flask_cors import cross_origin

users_bp = Blueprint('users', __name__)

@users_bp.route('/add_user', methods=['POST'])
@cross_origin()
def add_user():
    try:
        body = request.get_json()

        if not body:
            return jsonify({"error": "Missing request body"}), 400

        username = body.get('username')
        password = body.get('password')
        is_admin = body.get('admin', False)

        if not username or not password:
            return jsonify({"error": "Missing required values in the request body"}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        with DatabaseConnection() as (conn, cursor):
            insert_query = """
            INSERT INTO users (username, password, admin)
            VALUES (%s, %s, %s);
            """
            cursor.execute(insert_query, (username, hashed_password, is_admin))
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID() AS id;")
            result = cursor.fetchone()
            inserted_id = result['id'] if result else None

        return jsonify({
            "message": "User added successfully.",
            "id": inserted_id
        }), 200

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500

