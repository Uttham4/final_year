from flask import Blueprint, request, jsonify
import json
from utils import DatabaseConnection, serialize_data
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_cors import cross_origin

students_bp = Blueprint('students', __name__)

UPLOAD_FOLDER = "uploads/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


students_bp = Blueprint('students', __name__)

# POST -- Get student details
@students_bp.route('/student_details', methods=['POST'])
@cross_origin()
def student_details():
    try:
        body = request.get_json()
        if not body or 'id' not in body:
            return jsonify({"error": "Missing 'id' in the request body"}), 400

        student_id = body['id']

        with DatabaseConnection() as (conn, cursor):
            # Fetch student type
            cursor.execute("SELECT type FROM student_details WHERE roll_num = %s;", (student_id,))
            student_type = cursor.fetchone()
            cursor.fetchall()  # Clear unread results

            if not student_type:
                return jsonify({"error": "Student not found"}), 404

            # Check 'today' and 'paid' fields
            cursor.execute("SELECT today, paid,last_menu FROM student_details WHERE roll_num = %s;", (student_id,))
            student_values = cursor.fetchone()
            last_menu = student_values.get("last_menu")
            try:
                last_menu = json.loads(last_menu) if last_menu else {}
            except json.JSONDecodeError:
                last_menu = {}
            cursor.fetchall()  # Clear unread results
            print("student_values['type'].upper()",student_type['type'].upper())

            if student_type['type'].upper() == "DAY SCHOLAR" and student_values['paid'] == 1:
                return jsonify({"message": "paid", "menu": last_menu}), 200

            if student_type['type'].upper() == "HOSTELLER" and student_values['today'] == 1:
                return jsonify({"message": "Already marked today"}), 200
            if student_type['type'].upper() == "HOSTELLER":
                update_today="UPDATE student_details SET today = 1 WHERE roll_num = %s;"
                cursor.execute(update_today, (student_id,))
                conn.commit()

            # Fetch student details
            select_query = """
                SELECT first_name, last_name, reg_num, roll_num, type, department, age,
                       contact_number, email, image, paid, address, year, section, semester,history
                FROM student_details 
                WHERE roll_num = %s;
            """
            cursor.execute(select_query, (student_id,))
            student_data = cursor.fetchall()
            cursor.fetchall()  # Clear unread results

        return jsonify(json.loads(json.dumps(student_data, default=serialize_data))), 200

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500

@students_bp.route('/update_today', methods=['POST'])
@cross_origin()
def update_today():
    try:
        body = request.get_json()
        if not body or 'id' not in body:
            return jsonify({"error": "Missing 'id' in the request body"}), 400

        student_id = body['id']

        with DatabaseConnection() as (conn, cursor):
            # Fetch student type
            cursor.execute("UPDATE student_details SET today = 1 WHERE roll_num = %s;", (student_id,))
            conn.commit()


        return jsonify({"message":"student marked for today successfully"}), 200

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500



# GET -- Count students marked today
@students_bp.route('/count_student', methods=['GET'])
@cross_origin()
def count_student():
    try:
        with DatabaseConnection() as (conn, cursor):
            # Count all students where today = 1
            cursor.execute("SELECT COUNT(*) AS total_count FROM student_details WHERE today = 1;")
            total_count = cursor.fetchone()

            # Count DAY SCHOLAR students where today = 1
            cursor.execute("SELECT COUNT(*) AS day_scholar_count FROM student_details WHERE today = 1 AND UPPER(type) = 'DAY SCHOLAR';")
            day_scholar_count = cursor.fetchone()

            # Count HOSTELLER students where today = 1
            cursor.execute("SELECT COUNT(*) AS hosteller_count FROM student_details WHERE today = 1 AND UPPER(type) = 'HOSTELLER';")
            hosteller_count = cursor.fetchone()

        return jsonify({
            "total_count": total_count['total_count'] if total_count else 0,
            "day_scholar_count": day_scholar_count['day_scholar_count'] if day_scholar_count else 0,
            "hosteller_count": hosteller_count['hosteller_count'] if hosteller_count else 0
        }), 200

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500


# POST -- Add new student
@students_bp.route('/add_student', methods=['POST'])
@cross_origin()
def add_student():
    try:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        reg_num = request.form.get('reg_num')
        roll_num = request.form.get('roll_num')
        student_type = request.form.get('type')
        year = request.form.get('year')
        semester = request.form.get('semester')
        department = request.form.get('department')
        section = request.form.get('section')
        age = request.form.get('age')

        if not first_name or not last_name or not reg_num or not roll_num:
            return jsonify({"error": "Missing required values"}), 400

        # Handle Image Upload
        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(image_path)

        with DatabaseConnection() as (conn, cursor):
            insert_query = """
            INSERT INTO student_details (
                roll_num, reg_num, first_name, last_name, type, year, semester, 
                department, section, age, image
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
            """
            cursor.execute(insert_query, (roll_num, reg_num, first_name, last_name, student_type, year, semester, department, section, age, image_path))
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID() AS id;")
            result = cursor.fetchone()
            inserted_id = result['id'] if result else None

        return jsonify({"message": "Student added successfully.", "id": inserted_id}), 200

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500