from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from connect_db import connect_db, Error



app = Flask(__name__)
app.json.sort_keys = False #maintain order of your stuff

ma = Marshmallow(app)



class MemberSchema(ma.Schema):
    member_id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    bench_amount = fields.Int(required=True)
    membership_type = fields.String(required=True)

    class Meta:  
        
        fields = ("member_id", "name", "email", "phone", "bench_amount", "membership_type")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

@app.route('/')
def home():
    return "Welcome to our super cool Fitness Tracker, time to get swole brah!"

@app.route('/members', methods=['GET'])
def get_members(): 
    print("hello from the get")  
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True)
        # SQL query to fetch all members
        query = "SELECT * FROM Members"

        # executing query with cursor
        cursor.execute(query)

        # accessing stored query
        members = cursor.fetchall()

         # use Marshmallow to format the json response
        return members_schema.jsonify(members)
    
    except Error as e:
        # error handling for connection/route issues
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


#                          to create or send data to our server
@app.route('/members', methods = ['POST']) 
def add_member():
    try:
        # Validate the data follows our structure from the schema
        # deserialize the data using Marshmallow
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"Error": "Database connection failed"}), 500
        cursor = conn.cursor()

        # new customer details, to be sent to our db
        # comes from customer_data which we turn into a python dictionary
        # with .load(request.json)
        new_member = (member_data['name'], member_data['email'], member_data['phone'], member_data['bench_amount'], member_data['membership_type'])

        # SQL Query to insert customer data into our database
        query = "INSERT INTO Members (name, email, phone, bench_amount, membership_type) VALUES(%s, %s, %s, %s, %s)"

        # execute the query 
        cursor.execute(query, new_member)
        conn.commit()

        # Succesfiul addition of our customer
        return jsonify({"message":"New member added succesfully"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 

@app.route('/members/<int:id>', methods= ["PUT"])
def update_member(id):
    try:
        # Validate the data follows our structure from the schema
        # deserialize the data using Marshmallow
        # this gives us a python dictionary
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        # Updating customer info
        updated_member = (member_data['name'], member_data['email'], member_data['phone'], member_data['bench_amount'], member_data['membership_type'], id)

        # SQL Query to find and update a customer based on the id
        query = "UPDATE Members SET name = %s, email = %s, phone = %s, bench_amount = %s, membership_type = %s WHERE member_id = %s"

        # Executing Query
        cursor.execute(query, updated_member)
        conn.commit()

        # Message for succesful update
        return jsonify({"message":"Member details were succesfully updated!"}), 200
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/members/<int:id>', methods=["DELETE"])
def delete_customer(id):
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        member_to_remove = (id,)

        # query to find member based on their id
        query = "SELECT * FROM members WHERE member_id = %s"
        # check if customer exists in db
        cursor.execute(query, member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "Database connection Failed, user does not exist"}), 500
        
        # If member exists, we shall delete them :( 
        del_query = "DELETE FROM members WHERE member_id = %s"
        cursor.execute(del_query, member_to_remove)
        conn.commit()

        # nice message about the execution of our beloved customer
        return jsonify({"message":"Member Removed succesfully"}), 200   



    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 

# ================= dank_sesh SCHEMA and ROUTES ============================
class SeshSchema(ma.Schema):
    sesh_id = fields.Int(dump_only=True)
    member_id = fields.Int(required=True)
    date = fields.Date(required=True)
    workout_type = fields.Str(required=True)
    class Meta:  
        fields = ("sesh_id", "member_id", "date", "workout_type")

# initialize our schemas
sesh_schema = SeshSchema()
seshs_schema = SeshSchema(many=True)


@app.route("/dank_sesh", methods = ["GET"])
def get_seshs():
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM dank_sesh"
        cursor.execute(query)
        seshs = cursor.fetchall()  

        return seshs_schema.jsonify(seshs)
    
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 

# POST request to add seshs
@app.route('/dank_sesh', methods=["POST"])
def add_seshs():
    try:
        # Validate incoming data
        sesh_data = sesh_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        
        query = "INSERT INTO Dank_sesh (date, member_id, workout_type) VALUES (%s,%s,%s)"
        cursor.execute(query, (sesh_data['date'], sesh_data['member_id'], sesh_data["workout_type"]))
        conn.commit()
        return jsonify({"message": "That Dank Sesh was succesfully added bruh"}),201

    

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
    #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 


# PUT request to Update Order
@app.route('/dank_sesh/<int:sesh_id>', methods= ["PUT"])
def update_sesh(sesh_id):
    try:
        # Validate incoming data
        sesh_data = sesh_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        query = "UPDATE Dank_sesh SET date = %s, member_id = %s, workout_type = %s WHERE sesh_id = %s"
        cursor.execute(query, (sesh_data['date'], sesh_data['member_id'], sesh_data['workout_type'], sesh_id))
        conn.commit()
        return jsonify({"message": "That Dank Sesh updated succesfully bruh"}), 200

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
    #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()




if __name__ == "__main__":
    app.run(debug=True)