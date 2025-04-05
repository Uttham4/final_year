from flask import Flask,Blueprint, request, jsonify
import mysql.connector
import requests
from razorpay import Client
from flask_cors import CORS
import json
import logging
from utils import DatabaseConnection


payments_bp = Blueprint('payments', __name__)


def send_to_esp32(url, servo_degree):
    import requests
    try:
        payload = {"servo_degree": servo_degree}
        response = requests.post(url, json=payload, timeout=5)
        print(f"Response status: {response.status_code}, Response text: {response.text}")
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with ESP32: {e}")
        return 500, str(e)


@payments_bp.route('/control_servo', methods=['POST'])
def control_servo():
    try:
        data = request.get_json()
        print("data",data)
        if not data or 'servo_degree' not in data:
            return "Invalid data received", 400

        servo_degree = data['servo_degree']
        esp32_url = "https://55ff-2409-40f4-2f-1f60-3d6b-a086-ecb2-5e10.ngrok-free.app/update_servo"

        status_code, response_text = send_to_esp32(esp32_url, servo_degree)
        if status_code == 200:
            return "Servo position updated successfully", 200
        else:
            return f"Failed to update servo position: {response_text}", status_code
    except Exception as e:
        return f"Server error: {str(e)}", 500






# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Razorpay client configuration
KEY_ID = 'rzp_test_L3zRDHReH9Csk5'
KEY_SECRET = 'XJiNYd1BDWwhBdFKJ8axV6I8'
client = Client(auth=(KEY_ID, KEY_SECRET))


# Route to create an order
@payments_bp.route('/create_order', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        amount = data.get('amount', 100)
        print("amount",amount,type(amount))
        currency = data.get('currency', 'INR')

        order_data = {
            'amount': int(amount),
            'currency': currency,
            'payment_capture': 1
        }

        order = client.order.create(data=order_data)
        logger.info(f"Created order: {order}")
        return jsonify(order), 200

    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Route to verify payment
@payments_bp.route('/verify_payment', methods=['POST'])
def verify_payment():
    try:
        data = request.get_json()

        # Extract required fields
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')
        student_id = data.get('student_id')

        if not all([payment_id, order_id, signature, student_id]):
            return jsonify({'status': 'failed', 'message': 'Missing required parameters'}), 400

        params_dict = {
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        }

        # Verify payment signature
        client.utility.verify_payment_signature(params_dict)

        # Update payment status in the database
        
        return jsonify({'status': 'success', 'message': 'Payment verified and database updated'}), 200


    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500




# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def update_payment_status(student_id: int, menu: dict,amount) -> bool:
    """Update the payment status in the database."""
    try:
        print(f"Updating student ID {student_id} with amount {amount}")
        with DatabaseConnection() as (conn, cursor):
            update_query = """
                UPDATE student_details
                SET history = CONCAT(
                    IFNULL(history, ''), 
                    NOW(), 
                    ' - Amount: ', 
                    %s, 
                    '\n'
                ), 
                paid = TRUE,
                last_menu = %s
                WHERE roll_num = %s;
            """
            menu_json = json.dumps(menu)  # Convert menu dict to JSON string
            cursor.execute(update_query, (int(amount), menu_json, student_id))
            affected_rows = cursor.rowcount  # Store before closing cursor
            conn.commit()

        print(f"Affected rows: {affected_rows}")
        return affected_rows > 0

    except Exception as err:
        logger.error(f"Database update failed: {err}")
        return False




@payments_bp.route('/payment_handler', methods=['POST'])
def payment_handler():
    """Handles payment verification and updates the database."""
    try:
        body = request.get_json()
        if not body or 'student_id' not in body:
            return jsonify({"error": "Missing 'student_id' in request body"}), 400

        student_id = body['student_id']
        menu = body.get('menu')
        amount = body.get('amount',100)

        if update_payment_status(student_id,menu,amount):
            logger.info(f"Payment status updated for student: {student_id}")
            return jsonify({"message": "Payment verified and database updated"}), 200
        else:
            logger.error(f"Database update failed for student: {student_id}")
            return jsonify({"error": "Database update failed"}), 500

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": f"Database update failed: {str(e)}"}), 500


@payments_bp.route('/update_paid_status', methods=['POST'])
def update_paid_status():
    """Update the 'paid' status in the database."""
    try:
        body = request.get_json()
        if not body or 'id' not in body:
            return jsonify({"error": "Missing 'id' in request body"}), 400

        student_id = body['id']

        with DatabaseConnection() as (conn, cursor):
            update_query = "UPDATE student_details SET paid = FALSE, last_menu = NULL WHERE roll_num = %s;"
            cursor.execute(update_query, (student_id,))
            conn.commit()


        return jsonify({"message": "Payment status updated successfully"}), 200

    except Exception as err:
        logger.error(f"Database update failed: {err}")
        return jsonify({"error": "Database update failed"}), 500
