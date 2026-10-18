import base64
import json 
import os 
from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError 
from model import db, Book, Category

books_bp = Blueprint('routes', __name__)

ALLOWED_SORT = {
    'id': Book.id,
    'price_vnd': Book.price_vnd,
    'title': Book.title,
    'stock': Book.stock
}

schema_path = os.path.join(os.path.dirname(__file__), 'books_schema.json')
with open(schema_path, 'r', encoding='utf-8') as f:
    BOOK_SCHEMA = json.load(f)

def encode_cursor(data):
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip('=')

def decode_cursor(raw):
    try:
        pad = '=' * (-len(raw) % 4)
        return json.loads(base64.urlsafe_b64decode((raw + pad).encode()).decode())
    except Exception:
        return None

def parse_multi_sort(sort_str):
    sort_cols = []
    has_id = False
    for item in sort_str.split(','):
        item = item.strip()
        if not item:
            continue
        desc = item.startswith('-')
        key = item.lstrip('-')
        if key not in ALLOWED_SORT:
            return None, f"Sort key '{key}' không hợp lệ"
        if key == 'id':
            has_id = True
        col = ALLOWED_SORT[key]
        sort_cols.append(col.desc() if desc else col.asc())

    if not has_id:
        sort_cols.append(Book.id.asc())
    return sort_cols, None

@books_bp.route('/api/v1/books', methods=['GET'])
def list_books():
    strategy = request.args.get('strategy', 'cursor').lower()
    genre = request.args.get('genre')
    sort_raw = request.args.get('sort', 'id')
    limit = min(request.args.get('limit', 20, type=int), 100)

    sort_cols, error = parse_multi_sort(sort_raw)
    if error:
        return jsonify({"error": error}), 400

    query = Book.query
    if genre:
        query = query.join(Book.category).filter(Category.slug == genre)

    if strategy == 'offset':
        page = max(request.args.get('page', 1, type=int), 1)
        total = query.count()
        items = query.order_by(*sort_cols).offset((page - 1) * limit).limit(limit).all()

        return jsonify({
            "strategy": "offset",
            "data": [b.to_dict() for b in items],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_next": (page * limit) < total
            }
        })

    elif strategy == 'cursor':
        cursor_raw = request.args.get('cursor')

        if cursor_raw:
            c_data = decode_cursor(cursor_raw)
            if not c_data or 'id' not in c_data:
                return jsonify({"error": "Cursor không hợp lệ"}), 400

            p_key = list(c_data.keys())[0]
            p_val, last_id = c_data[p_key], c_data['id']
            p_col = ALLOWED_SORT.get(p_key, Book.id)
            is_desc = sort_raw.startswith('-')

            if is_desc:
                query = query.filter((p_col < p_val) | ((p_col == p_val) & (Book.id > last_id)))
            else:
                query = query.filter((p_col > p_val) | ((p_col == p_val) & (Book.id > last_id)))

        items = query.order_by(*sort_cols).limit(limit + 1).all()
        has_next = len(items) > limit
        items = items[:limit]

        next_cursor = None
        if items and has_next:
            last = items[-1]
            p_key = sort_raw.lstrip('-').split(',')[0]
            next_cursor = encode_cursor({
                p_key: getattr(last, p_key, last.id),
                "id": last.id
            })

        return jsonify({
            "strategy": "cursor",
            "data": [b.to_dict() for b in items],
            "pagination": {
                "limit": limit,
                "has_next": has_next,
                "next_cursor": next_cursor
            }
        })

    return jsonify({"error": "Strategy không hỗ trợ. Dùng 'offset' hoặc 'cursor'"}), 400

@books_bp.route('/api/v1/books', methods=['POST'])
def create_book():
    payload = request.get_json(silent=True) or {}
    try:
        validate(instance=payload, schema=BOOK_SCHEMA)
    except ValidationError as e:
        return jsonify({"error": "validation_failed", "message": e.message}), 400

    new_book = Book(
        title=payload['title'],
        isbn=payload['isbn'],
        price_vnd=payload['price_vnd'],
        stock=payload.get('stock', 0),
        category_id=payload.get('category_id')
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify(new_book.to_dict()), 201