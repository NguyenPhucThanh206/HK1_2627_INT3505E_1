from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)
"""
STUDENTS = []

@app.route("/students", methods=["POST"])
def create_student():
    body = request.get_json(silent = True) or {}
    name = body.get("name")
    if not name:
        return jsonify({"error": "Name la bat buoc"}), 400
    student = {
        "id": str(uuid4()),
        "name": name,
        "gpa": body.get("gpa", 0.0),
    }

    STUDENTS.append(student)
    return jsonify(student), 201

@app.route("/books/<book_id>", methods = ["GET"])
def get_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(book), 200

@app.route("/items/<int:item_id>")
def get_item(item_id):
    return jsonify({"id":item_id}), 200

@app.route("/books", methods = ["GET"])
def list_books():
    limit = int(request.args.get("limit", 20))
    q = request.args.get("q","").strip().lower()
    return jsonify({"item": item}), 200
"""
"""
ORDERS = {
    "1": {"id": "1", "status": "pending"},
    "2": {"id": "2", "status": "shipped"},
    "3": {"id": "3", "status": "delivered"},
}  

@app.route("/orders/<order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = ORDERS.get(order_id)

    if order is None:
        return {"error": "not found"}, 404

    if order["status"] in ("shipped", "delivered"):
        return {"error": "cannot delete"}, 409
    ORDERS.pop(order_id, None)
    return "", 204
"""

app = Flask(__name__)
_next_id = 3

STUDENTS = [
    {"id": 1, "student_code": "SV001", "name": "DO CONG BAN", "gpa": 3.2, "year": 2000},
    {"id": 2, "student_code": "SV002", "name": "DO CONG HUNG", "gpa": 3.8, "year": 2002}
]

def find_student(sid):
    return next((s for s in STUDENTS if s["id"] == sid), None)

@app.route("/students", methods=["GET"])
def list_students():
    result = list(STUDENTS)

    q = request.args.get("q", "").strip().lower()
    if q:
        result = [s for s in result if q in s["name"].lower() or q in s["student_code"].lower()]

    sort_by = request.args.get("sort", "").strip().lower()
    if sort_by in ["name", "gpa", "year", "student_code"]:
        result = sorted(result, key=lambda s: s[sort_by])

    limit = request.args.get("limit", type=int)
    if limit:
        result = result[:limit]
        
    return jsonify(result), 200

@app.route("/students/<int:sid>", methods=["GET"])
def get_student(sid):
    student = find_student(sid)
    if not student:
        return jsonify({"error": "student not found"}), 404
    return jsonify(student), 200

@app.route("/students", methods=["POST"])
def create_student():
    global _next_id
    body = request.get_json(silent=True) or {}
    
    name = body.get("name")
    student_code = body.get("student_code")
    gpa = body.get("gpa", 0.0)
    year = body.get("year")
    
    if not name or not student_code:
        return jsonify({"error": "need name and student_code"}), 400
        
    if year is None:
        return jsonify({"error": "year is required"}), 400
    try:
        year = int(year)
        if year < 1900:
            return jsonify({"error": "year must be >= 1900"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "year must be an integer"}), 400
            
    student = {
        "id": _next_id,
        "student_code": str(student_code),
        "name": str(name),
        "gpa": float(gpa),
        "year": year
    }
    
    _next_id += 1
    STUDENTS.append(student)
    
    return jsonify(student), 201, {"Location": f"/students/{student['id']}"}

@app.route("/students/<int:sid>", methods=["PUT", "DELETE"])
def modify_student(sid):
    student = find_student(sid)
    if not student:
        return jsonify({"error": "student not found"}), 404
        
    if request.method == "PUT":
        body = request.get_json(silent=True) or {}
        
        if "year" in body and body["year"] is not None:
            try:
                year_val = int(body["year"])
                if year_val < 1900:
                    return jsonify({"error": "year must be >= 1900"}), 400
                body["year"] = year_val
            except (ValueError, TypeError):
                return jsonify({"error": "year must be an integer"}), 400
                
        student.update(body)
        return jsonify(student), 200
        
    STUDENTS.remove(student)
    return "", 204

if __name__ == "__main__":
    app.run(debug=True, port=5000)