from utils import *
import json
import bcrypt

def add_user(event, context):
    try:
        if 'body' not in event or event['body'] is None:
            return create_response(400, {"error": "Missing 'body' in event"})

        body = json.loads(event['body'])
        username = body.get('username')
        password = body.get('password')
        is_admin = body.get('admin', False)

        if not username or not password:
            return create_response(400, {"error": "Missing required values in the request body"})

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        with DatabaseConnection() as (conn, cursor):
            insert_query = """
            INSERT INTO users (
                username, password, admin
            ) VALUES (
                %s, %s, %s
            );
            """
            cursor.execute(insert_query, (username, hashed_password, is_admin))
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID() AS id;")
            result = cursor.fetchone()
            inserted_id = result['id'] if result else None

        return create_response(200, {
            "message": "User added successfully.",
            "id": inserted_id
        })

    except ValueError as ve:
        return create_response(400, {"error": str(ve)})

    except Exception as e:
        print("Exception occurred:", e)
        return create_response(500, {"error": "Internal server error"})
