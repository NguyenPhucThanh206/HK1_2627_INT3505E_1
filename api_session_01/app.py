from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)