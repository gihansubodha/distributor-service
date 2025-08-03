import os
print("Running Distributor API from:", __file__)

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from db_config import get_db_connection

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}}, allow_headers="*")

@app.after_request
def apply_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

#  GET Distributor Stock
@app.route('/stock/<int:distributor_id>', methods=['GET'])
def get_distributor_stock(distributor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM distributor_stock WHERE distributor_id=%s", (distributor_id,))
    stock = cursor.fetchall()
    conn.close()
    return jsonify(stock)

#  ADD New Stock Item
@app.route('/stock', methods=['POST'])
def add_distributor_stock():
    data = request.json
    distributor_id = data['distributor_id']
    blanket_model = data['blanket_model']
    quantity = data['quantity']
    min_required = data.get('min_required', 10)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO distributor_stock (distributor_id, blanket_model, quantity, min_required) VALUES (%s, %s, %s, %s)",
                   (distributor_id, blanket_model, quantity, min_required))
    conn.commit()
    conn.close()
    return jsonify({"msg": "Distributor stock item added"})

#  UPDATE Stock Quantity
@app.route('/stock/<int:stock_id>', methods=['PUT'])
def update_distributor_stock(stock_id):
    data = request.json
    quantity = data['quantity']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE distributor_stock SET quantity=%s WHERE id=%s", (quantity, stock_id))
    conn.commit()
    conn.close()
    return jsonify({"msg": "Distributor stock updated"})

#  DELETE Stock Item
@app.route('/stock/<int:stock_id>', methods=['DELETE'])
def delete_distributor_stock(stock_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM distributor_stock WHERE id=%s", (stock_id,))
    conn.commit()
    conn.close()
    return jsonify({"msg": "Distributor stock item deleted"})

#  GET Seller Requests (Dashboard)
@app.route('/seller-requests/<int:distributor_id>', methods=['GET'])
def get_seller_requests(distributor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM seller_requests WHERE distributor_id=%s ORDER BY created_at DESC", (distributor_id,))
    requests = cursor.fetchall()
    conn.close()
    return jsonify(requests)

#  UPDATE Seller Request Status
@app.route('/seller-requests/<int:request_id>', methods=['PUT'])
def update_seller_request_status(request_id):
    data = request.json
    status = data['status']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE seller_requests SET status=%s WHERE id=%s", (status, request_id))
    conn.commit()
    conn.close()
    return jsonify({"msg": "Seller request status updated"})

# SEND Stock Request to Manufacturer
@app.route('/request-manufacturer', methods=['POST'])
def request_manufacturer():
    data = request.json
    distributor_id = data['distributor_id']
    blanket_model = data['blanket_model']
    quantity = data['quantity']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO distributor_requests (distributor_id, blanket_model, quantity) VALUES (%s, %s, %s)",
                   (distributor_id, blanket_model, quantity))
    conn.commit()
    conn.close()
    return jsonify({"msg": "Stock request sent to manufacturer"})

# CHECK Low Stock
@app.route('/check-low-stock/<int:distributor_id>', methods=['GET'])
def check_low_stock(distributor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM distributor_stock WHERE distributor_id=%s AND quantity < min_required", (distributor_id,))
    low_stock = cursor.fetchall()
    conn.close()
    return jsonify({"low_stock": low_stock})

@app.route('/all', methods=['GET'])
def get_all_distributors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username AS name FROM users WHERE role='distributor'")
    distributors = cursor.fetchall()
    conn.close()
    return jsonify(distributors)

@app.route('/routes', methods=['GET'])
def list_routes():
    return jsonify([rule.rule for rule in app.url_map.iter_rules()])

#  Health check
@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "Distributor Service Running"})


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
