from utils import *
import json


# POST -- to get student details
def student_details(event, context):
    try:
        if 'body' not in event or event['body'] is None:
            return create_response(400, {"error": "Missing 'body' in event"})

        body = json.loads(event['body'])
        student_id = body.get('id')
        if not student_id:
            return create_response(400, {"error": "Missing 'id' in the request body"})

        with DatabaseConnection() as (conn, cursor):

            type_query="select type from student_details where roll_num = %s;"
            cursor.execute(type_query,(student_id,))
            type=cursor.fetchone()
            print("type",type)
            cursor.fetchall()

            # First Query: Checking 'today' and 'paid'
            today_query = "SELECT today, paid FROM student_details WHERE roll_num = %s;"
            cursor.execute(today_query, (student_id,))
            today = cursor.fetchone()

            print("today", today)

            # **Clear Unread Results**
            cursor.fetchall()

            if type['type']=="day scholar":
                if today['paid'] == 1:
                    return create_response(200, {"message": "paid"})
            
            if type['type']!="day scholar":
                if today['today'] == 1:
                    return create_response(200, {"message": "Already marked today"})


            # Second Query: Fetching Student Details
            select_query = """
                SELECT first_name, last_name, reg_num, roll_num, type, department, age,
                       contact_number, email, image, paid, address, year, section, semester
                FROM student_details 
                WHERE roll_num = %s;
            """
            cursor.execute(select_query, (student_id,))
            data = cursor.fetchall()

            # **Clear Unread Results Again (Just in Case)**
            cursor.fetchall()

            # Third Query: Updating 'today' column
            update_query = "UPDATE student_details SET today = 1 WHERE roll_num = %s;"
            cursor.execute(update_query, (student_id,))
            conn.commit()

        serialized_data = json.dumps(data, default=serialize_data)
        return create_response(200, json.loads(serialized_data))

    except ValueError as ve:
        return create_response(400, {"error": str(ve)})

    except Exception as e:
        print("Exception occurred:", e)
        return create_response(500, {"error": "Internal server error"})




def count_student(event, context):
    try:
        with DatabaseConnection() as (conn, cursor):
            # First Query: Checking 'today' and 'paid'
            today_query = "SELECT count(*) FROM student_details WHERE today = 1;"
            cursor.execute(today_query)
            today = cursor.fetchone()  # Get the count from the query result
            print("today",today)
            
            # If the result is a tuple, the count will be the first element
            student_count = today['count(*)'] if today else 0

        # Return the count as a JSON response
        return create_response(200, {"count": student_count})

    except ValueError as ve:
        return create_response(400, {"error": str(ve)})

    except Exception as e:
        print("Exception occurred:", e)
        return create_response(500, {"error": "Internal server error"})





def testing_query(event, context):
    try:
        print(event)
        if 'body' not in event or event['body'] is None:
            return create_response(400, {"error": "Missing 'body' in event"})

        body = json.loads(event['body'])
        query = body.get('query')


        with DatabaseConnection() as (conn, cursor):

            cursor.execute(query)
            data = cursor.fetchall()
            conn.commit()
            print(data)


        return create_response(200, {
            "message": "success",
        })

    except ValueError as ve:
        return create_response(400, {"error": str(ve)})

    except Exception as e:
        print("Exception occurred:", e)
        return create_response(500, {"error": "Internal server error"})




# POST  -- to add new student
def add_student(event, context):
    try:
        if 'body' not in event or event['body'] is None:
            return create_response(400, {"error": "Missing 'body' in event"})

        body = json.loads(event['body'])
        first_name = body.get('first_name')
        last_name = body.get('last_name')
        reg_num = body.get('reg_num')
        roll_num = body.get('roll_num')
        student_type = body.get('type')

        if not first_name or not last_name or not reg_num:
            return create_response(400, {"error": "Missing required values in the request body"})

        with DatabaseConnection() as (conn, cursor):
            insert_query = """
            INSERT INTO student_details (
                roll_num, reg_num, first_name, 
                last_name, type
            ) VALUES (
                %s, %s, %s, %s, %s
            );
            """
            cursor.execute(insert_query, (roll_num, reg_num, first_name, last_name, student_type))
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID() AS id;")
            result = cursor.fetchone()
            inserted_id = result['id'] if result else None

        return create_response(200, {
            "message": "Student added successfully.",
            "id": inserted_id
        })

    except ValueError as ve:
        return create_response(400, {"error": str(ve)})

    except Exception as e:
        print("Exception occurred:", e)
        return create_response(500, {"error": "Internal server error"})
