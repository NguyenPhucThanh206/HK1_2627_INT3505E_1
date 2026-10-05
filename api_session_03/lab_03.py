import base64
from flask import Flask, jsonify, request 

app = Flask(__name__)

orders_db = [
    {"id": 1, "customer_id": 101, "status": "paid", "total": 360.0, "created_at": "2026-01-10"},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 361.0, "created_at": "2026-01-10"},
    {"id": 3, "customer_id": 103, "status": "paid", "total": 362.0, "created_at": "2026-01-10"},
    {"id": 4, "customer_id": 104, "status": "cancelled", "total": 363.0, "created_at": "2026-01-10"},
    {"id": 5, "customer_id": 102, "status": "paid", "total": 364.0, "created_at": "2026-01-10"},
    {"id": 6, "customer_id": 103, "status": "pending", "total": 365.0, "created_at": "2026-01-10"}
]

def decode_cursor(cursor_str):
    try:
        decoded_bytes = base64.b64decode(cursor_str.encode("utf-8"))
        return int(decoded_bytes.decode("utf-8"))
    except Exception:
        return None

def encode_cursor(last_id):
    return base64.b64encode(str(last_id).encode("utf-8")).decode("utf-8")

@app.get("/orders")
def get_orders():
    status_filter = request.args.get("status")
    customer_id_filter = request.args.get("customer_id")
    sort_param = request.args.get("sort")
    fields_param = request.args.get("fields")
    cursor_param = request.args.get("cursor")
    limit = request.args.get("limit", default=5, type=int)

    filtered_orders = list(orders_db)

    if status_filter:
        filtered_orders = [o for o in filtered_orders if o["status"] == status_filter]
    if customer_id_filter:
        filtered_orders = [o for o in filtered_orders if str(o["customer_id"]) == str(customer_id_filter)]

    if sort_param:
        reverse = sort_param.startswith("-")
        sort_field = sort_param.lstrip("-")
        if filtered_orders and sort_field in filtered_orders[0]:
            filtered_orders.sort(key=lambda x: x[sort_field], reverse=reverse)

    if cursor_param:
        last_id = decode_cursor(cursor_param)
        if last_id is None:
            return jsonify({
                "type": "https://api.example.com/probs/invalid-cursor",
                "title": "Bad Request",
                "status": 400,
                "detail": "Cursor khong hop le hoac bi loi dinh dang Base64",
                "instance": request.path
            }), 400, {"Content-Type": "application/problem+json"}
        
        filtered_orders = [o for o in filtered_orders if o["id"] > last_id]

    has_more = len(filtered_orders) > limit
    paginated_orders = filtered_orders[:limit]

    next_cursor = None
    if paginated_orders and has_more:
        last_item_id = paginated_orders[-1]["id"]
        next_cursor = encode_cursor(last_item_id)

    if fields_param:
        selected_fields = [f.strip() for f in fields_param.split(",")]
        result_data = [
            {k: v for k, v in order.items() if k in selected_fields}
            for order in paginated_orders
        ]
    else:
        result_data = paginated_orders

    return jsonify({
        "status": "success",
        "data": result_data,
        "limit": limit,
        "next_cursor": next_cursor
    })

if __name__ == "__main__":
    app.run(debug=True)