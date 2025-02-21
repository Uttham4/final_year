import json
import os
import logging
from typing import Dict, Any
from utils import *
# import requests
import time



# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)





def update_payment_status(student_id: str) -> bool:
    """Update the payment status in the database."""
    try:
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
                paid = TRUE 
                WHERE id = %s;
            """

            cursor.execute(update_query, (100, student_id))
            conn.commit()
            cursor.close()
            return True
    except Exception as err:
        logger.error(f"Database update failed: {err}")
        return False




def payment_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        student_id = body.get('student_id')     
        
        try:

            # Update payment status
            if update_payment_status(student_id):
                logger.info(f"Payment status updated for student: {student_id}")

                return create_response(200,'Payment verified and database updated')
            else:
                logger.error(f"Database update failed for student: {student_id}")
                return create_response(500,'Database update failed')
            
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            return create_response(500,f'Database update failed : {str(e)}')
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_response(500,f'Database update failed : {str(e)}')
    



def update_paid_status(event, context):
    """Update the paid status in the database."""
    try:
        if 'body' not in event or event['body'] is None:
            return create_response(400, {"error": "Missing 'body' in event"})

        body = json.loads(event['body'])
        student_id = body.get('id')
        if not student_id:
            return create_response(400, {"error": "Missing 'id' in the request body"}) 
        with DatabaseConnection() as (conn, cursor):

            update_query = """
                UPDATE student_details
                SET paid = FALSE 
                WHERE id = %s;
            """

            cursor.execute(update_query, (student_id,))
            conn.commit()
            cursor.close()
            return True
    except Exception as err:
        logger.error(f"Database update failed: {err}")
        return False

