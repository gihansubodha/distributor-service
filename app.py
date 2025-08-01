from flask import Flask, request, jsonify
import jwt
from functools import wraps
from db_config import get_connection
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
AUTH_SECRET = "your_auth_secret"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").split(" ")[-1]
        if not token:
            return jsonify({"message": "Token required"}), 401
        try:
            jwt.decode(token, AUTH_SECRET, algorithms=["HS256"])
        except:
            return jsonify({"message": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/inventory", methods=["GET"])
@token_required
def get_inventory():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventory")
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

@app.route("/inventory", methods=["POST"])
@token_required
def add_inventory():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inventory (name, stock, min_stock) VALUES (%s, %s, %s)",
                   (data["name"], data["stock"], data["min_stock"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Inventory added"}), 201

@app.route("/seller_orders", methods=["GET"])
@token_required
def get_seller_orders():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM distributor_orders")
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

@app.route("/seller_orders/<int:order_id>", methods=["PUT"])
@token_required
def update_seller_order(order_id):
    status = request.json.get("status")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE distributor_orders SET status=%s WHERE id=%s", (status, order_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Seller order updated"})

@app.route("/request_stock", methods=["POST"])
@token_required
def request_from_manufacturer():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO manufacturer_orders (blanket_name, quantity, status) VALUES (%s, %s, %s)",
                   (data["blanket_name"], data["quantity"], "pending"))
    conn.commit()
    conn.close()
    return jsonify({"message": "Request sent to manufacturer"})
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
