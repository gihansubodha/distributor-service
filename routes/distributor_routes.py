from flask import request, jsonify
from app import app
from db_config import get_connection

@app.route('/')
def home():
    return "Distributor Service API is running!"

@app.route("/inventory", methods=["GET"])
def get_inventory():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM distributor_inventory")
        data = cursor.fetchall()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/inventory", methods=["POST"])
def add_inventory():
    data = request.json
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO distributor_inventory (blanket_model, quantity, location) VALUES (%s, %s, %s)", 
                       (data["blanket_model"], data["quantity"], data["location"]))
        conn.commit()
        return jsonify({"message": "Inventory added successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})
