from flask import Flask, jsonify, request, make_response, g
import sqlite3

app = Flask(__name__)
DB_FILE = 'library.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_FILE)
        
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT,
                price REAL
            )
        ''')
        db.commit()

@app.get("/books")
def list_books():
    db = get_db()
    rows = db.execute("SELECT * FROM books").fetchall()
    books_list = [dict(r) for r in rows]

    return jsonify({
        "data": books_list,
        "total": len(books_list)
    }), 200

@app.post("/books")
def create_book():
    if not request.is_json:
        return jsonify(error="expected JSON"), 415
    p = request.get_json(silent=True) or {}
    t = (p.get("title") or "").strip()
    a = (p.get("author") or "").strip()

    if not t or not a:
        return jsonify(error="title and author required"), 422

    db = get_db()

    cursor = db.execute(
        "INSERT INTO books (title, author) VALUES (?, ?)",
        (t, a)
    )
    db.commit()
    new_id = cursor.lastrowid
    book = {"id": new_id, "title": t, "author": a}
    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{book['id']}"
    return resp

@app.get("/books/<int:bid>")
def fetch(bid):
    db = get_db()
    row = db.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone() #dau ',' dang sau bid, truy van sqlite yeu cau tham so phai la tuple

    if row is None:
        return jsonify(error="not found"), 404

    resp = make_response(jsonify(dict(row)), 200)
    resp.headers["Cache-Control"] = "max-age=60"
    return resp

@app.put("/books/<int:bid>")
def put(bid):
    db = get_db()

    row = db.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
    if row is None:
        return jsonify(error="not found"), 404

    p = request.get_json(silent=True) or {}
    t, a = p.get("title"), p.get("author")

    if not t or not a:
        return jsonify(error="need title+author"), 422

    isbn = p.get("isbn")
    price = p.get("price")

    db.execute(
        "UPDATE books SET title = ?, author = ?, isbn = ?, price = ? WHERE id = ?", 
        (t.strip(), a.strip(), p.get("isbn"), p.get("price"), bid)
    )
    db.commit()

    update_row = db.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
    return jsonify(dict(update_row)), 200

@app.patch("/books/<int:bid>")
def patch(bid):
    db = get_db()
    row = db.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
    if row is None:
        return jsonify(error="not found"), 404

    p = request.get_json(silent=True) or {}

    if "price" in p and ((p.get("price")) is None or p.get("price") < 0):
        return jsonify(error="price must be positive"), 422

    fields = []
    params = []
    for key in ["title", "author", "isbn", "price"]:
        if key in p:
            fields.append(f"{key} = ?")
            params.append(p[key].strip() if isinstance(p[key], str) else p[key])

    if fields:
        query = f"UPDATE books SET {', '.join(fields)} WHERE id = ?"
        params.append(bid)
        db.execute(query, params)
        db.commit()
        
    updated_row = db.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
    return jsonify(dict(updated_row)), 200 

@app.delete("/books/<int:bid>")
def delete(bid):
    db = get_db()
    row = db.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
    if row is None:
        return jsonify(error="not found"), 404
        
    db.execute("DELETE FROM books WHERE id = ?", (bid,))
    db.commit()
    
    return "", 204

if __name__ == "__main__":
    init_db() 
    app.run(debug=True, port=5002)