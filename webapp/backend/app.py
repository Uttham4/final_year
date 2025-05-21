from flask import Flask, request, jsonify
import mysql.connector
import requests
import json
import logging
from razorpay import Client
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

db_config = {
    'host': 'localhost',
    'user': 'esp_user',
    'password': 'Welcome123',
    'database': 'esp32_data'
}


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


@app.route('/control_servo', methods=['POST'])
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



@app.route('/send_data', methods=['POST'])
def send_data():
    PIN_OUT = request.form.get("PIN_OUT")
    DEGREE = request.form.get("DEGREE")
    POSITION = request.form.get("POSITION")

    if PIN_OUT and DEGREE and POSITION:
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = "INSERT INTO esp32_data.servo_data (PIN_OUT, DEGREE, POSITION, DELETED_AT) VALUES (%s, %s, %s, NULL);"
            cursor.execute(query, (PIN_OUT, DEGREE, POSITION))
            conn.commit()
            return "Data inserted successfully", 200
        except Exception as e:
            return f"Database Error: {e}", 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return "No data received", 400





# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Razorpay client configuration
KEY_ID = ''
KEY_SECRET = ''
client = Client(auth=(KEY_ID, KEY_SECRET))


# Route to create an order
@app.route('/create_order', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        amount = data.get('amount', 100)
        currency = data.get('currency', 'INR')

        order_data = {
            'amount': amount,
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
@app.route('/verify_payment', methods=['POST'])
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




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

#  source myenv/bin/activate
# ssh -i "servo_key_pair.pem" ubuntu@18.218.182.119
# python3 app.py
# ngrok http 192.168.231.104:80
# https://70c1-110-224-88-204.ngrok-free.app

# To do when start :
#   - Start the ec2 instance and copy the public ip.
#   - Change the public ip in esp code, also in server starting command (ssh -i "servo_key_pair.pem" ubuntu@18.225.36.155), also in backend code of payment.py, also in index.js.
#   - Change the private ip of esp in ngrok.
#   - Start the xampp server and its sql client.