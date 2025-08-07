from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from db_config import get_db_connection

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

#  GET Distributor Stock
@app.route('/stock/<int:distributor_id>', methods=['GET'])
def get_distributor_stock(distributor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM distributor_stock WHERE distributor_id=%s", (distributor_id,))
    stock = cursor.fetchall()
    conn.close()
    return jsonify(stock)

#  ADD New Stock Item (with model_number, price)
@app.route('/stock', methods=['POST'])
def add_distributor_stock():
    data = request.json or {}
    distributor_id = data.get('distributor_id')
    blanket_model = data.get('blanket_model')
    model_number = data.get('model_number')       # optional
    price = data.get('price')                     # optional
    quantity = data.get('quantity', 0)
    min_required = data.get('min_required', 10)

    if not distributor_id or not blanket_model:
        return jsonify({"msg": "distributor_id and blanket_model are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO distributor_stock (distributor_id, blanket_model, model_number, price, quantity, min_required)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (distributor_id, blanket_model, model_number, price, quantity, min_required))
    conn.commit()
    conn.close()
    return jsonify({"msg": "Distributor stock item added"})

#  UPDATE Stock Quantity (kept simple)
@app.route('/stock/<int:stock_id>', methods=['PUT'])
def update_distributor_stock(stock_id):
    data = request.json or {}
    quantity = data.get('quantity')

    if quantity is None:
        return jsonify({"msg": "quantity is required"}), 400

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
    cursor.execute("""
        SELECT sr.*, u.username AS seller_name
        FROM seller_requests sr
        LEFT JOIN users u ON sr.seller_id = u.id
        WHERE sr.distributor_id=%s
        ORDER BY sr.created_at DESC
    """, (distributor_id,))
    requests = cursor.fetchall()
    conn.close()
    return jsonify(requests)

#  UPDATE Seller Request Status
@app.route('/seller-requests/<int:request_id>', methods=['PUT'])
def update_seller_request_status(request_id):
    data = request.json or {}
    status = data.get('status')
    if not status:
        return jsonify({"msg": "status is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE seller_requests SET status=%s WHERE id=%s", (status, request_id))
    conn.commit()
    conn.close()
    return jsonify({"msg": "Seller request status updated"})

#  SEND Stock Request to Manufacturer (unchanged payload)
@app.route('/request-manufacturer', methods=['POST'])
def request_manufacturer():
    data = request.json or {}
    distributor_id = data.get('distributor_id')
    blanket_model = data.get('blanket_model')
    quantity = data.get('quantity')

    if not distributor_id or not blanket_model or quantity is None:
        return jsonify({"msg": "distributor_id, blanket_model, quantity are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO distributor_requests (distributor_id, blanket_model, quantity)
        VALUES (%s, %s, %s)
    """, (distributor_id, blanket_model, quantity))
    conn.commit()
    conn.close()
    return jsonify({"msg": "Stock request sent to manufacturer"})

#  CHECK Low Stock
@app.route('/check-low-stock/<int:distributor_id>', methods=['GET'])
def check_low_stock(distributor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, blanket_model, model_number, price, quantity, min_required
        FROM distributor_stock
        WHERE distributor_id=%s AND quantity < min_required
    """, (distributor_id,))
    low_stock = cursor.fetchall()
    conn.close()
    return jsonify({"low_stock": low_stock})

#  List all distributors (for seller dropdown)
@app.route('/all', methods=['GET'])
def get_all_distributors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username AS name FROM users WHERE role='distributor'")
    distributors = cursor.fetchall()
    conn.close()
    return jsonify(distributors)

#  Health check
@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "Distributor Service Running"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
