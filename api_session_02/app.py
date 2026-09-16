from flask import Flask, jsonify, request, make_response
app = Flask(__name__)
BOOKS = []
_next_id = 1

@app.get("/books")
def list_books():
    return jsonify({
        "datas": BOOKS,
        "total": len(BOOKS)
    }), 200

@app.post("/books")
def create_book():
    global _next_id
    if not request.is_json:
        return jsonify(error="Expected JSON"), 415
    p = request.get_json(silent=True) or {}
    t = (p.get("title") or "").strip()
    a = (p.get("author") or "").strip()
    if not t or not a:
        return jsonify(error="Missing required fields"), 422
    
    book = {"id": _next_id, "title": t, "author": a}
    BOOKS.append(book)
    _next_id += 1
    resp = make_response(jsonify(book), 201)
    resp.headers["location"] = f"/books/{book['id']}"
    return resp

@app.get("/books/<int:id>")
def get_book(id):
    book = next((b for b in BOOKS if b["id"] == id), None)
    if not book:
        return jsonify(error="Book not found"), 404
    return jsonify(book), 200

if __name__ == "__main__":
    app.run(debug=True, port=5002)