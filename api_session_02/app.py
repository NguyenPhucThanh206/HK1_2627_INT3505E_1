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
                author TEXT NOT NULL
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

@app.get("/books/<int:id>")
def get_book(id):
    db = get_db()
   
    row = db.execute("SELECT * FROM books WHERE id = ?", (id,)).fetchone()
    if not row:
        return jsonify(error="Book not found"), 404
    return jsonify(dict(row)), 200

if __name__ == "__main__":
    init_db() 
    app.run(debug=True, port=5002)