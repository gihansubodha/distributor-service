# distributor_service/app.py
from flask import Flask, request, jsonify
from auth_utils import require_token,get_db
import mysql.connector

app = Flask(__name__)

@app.route("/inventory", methods=["GET","POST","PUT","DELETE"])
@require_token(role="distributor")
def inv():
    conn,cur=get_db(),get_db().cursor(dictionary=True)
    if request.method=="GET":
        cur.execute("SELECT * FROM inventory"); return jsonify(cur.fetchall())
    d=request.json
    if request.method=="POST":
        cur.execute("INSERT INTO inventory(name,quantity,min_stock) VALUES(%s,%s,%s)",
                    (d["name"],d["quantity"],d["min_stock"]))
        conn.commit(); return jsonify({"msg":"Added"}),201
    if request.method=="PUT":
        cur.execute("UPDATE inventory SET name=%s,quantity=%s,min_stock=%s WHERE id=%s",
                    (d["name"],d["quantity"],d["min_stock"],d["id"]))
        conn.commit(); return jsonify({"msg":"Updated"})
    if request.method=="DELETE":
        cur.execute("DELETE FROM inventory WHERE id=%s",(d["id"],))
        conn.commit(); return jsonify({"msg":"Deleted"})
    return "",400

@app.route("/orders", methods=["GET","POST","PUT"])
@require_token(role="distributor")
def dist_orders():
    conn,cur=get_db(),get_db().cursor(dictionary=True)
    if request.method=="GET":
        cur.execute("SELECT * FROM distributor_orders"); return jsonify(cur.fetchall())
    d=request.json
    if request.method=="POST":
        cur.execute("INSERT INTO distributor_orders(blanket_name,quantity,seller) VALUES(%s,%s,%s)",
                    (d["blanket_name"],d["quantity"],d["seller"]))
        conn.commit(); return jsonify({"msg":"Sent"}),201
    if request.method=="PUT":
        cur.execute("UPDATE distributor_orders SET status=%s WHERE id=%s",(d["status"],d["id"]))
        conn.commit(); return jsonify({"msg":"Updated"})
    return "",400

@app.route("/request_from_manufacturer", methods=["POST"])
@require_token(role="distributor")
def req_man():
    d=request.json
    import requests
    resp = requests.post("https://your-manufacturer-url/order_request", json=d, headers=request.headers)
    return jsonify(resp.json()), resp.status_code

if __name__=="__main__":
    app.run(debug=True)
