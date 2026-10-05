from flask import Flask, jsonify, request
app = Flask(__name__)

posts_db = [
    {"id": 1, "title": "First post", "content": "Lovely", "author_id": 101},
    {"id": 2, "title": "Second post", "content": "Still in love", "author_id": 102}
]

API_PREFIX = "/api/v1"

@app.route(f"{API_PREFIX}/posts", methods=["GET"])
def get_posts():
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    return jsonify({
        "status": "success",
        "page": page,
        "limit": limit,
        "total": len(posts_db),
        "data": posts_db[start_idx:end_idx]
    }), 200

@app.route(f"{API_PREFIX}/posts", methods=["POST"])
def create_post():
    data = request.get_json() or {}
    if not data.get("title") or not data.get("content"):
        return jsonify({"status": "error", "message": "Thieu title hoac content"}), 400
    new_post = {
        "id": posts_db[-1]["id"] + 1 if posts_db else 1,
        "title": data["title"],
        "content": data["content"],
        "author_id": data.get("author_id", 1)
    }
    posts_db.append(new_post)
    return jsonify({"status": "success", "data": new_post}), 201

@app.route(f"{API_PREFIX}/posts/<int:post_id>", methods = ["GET"])
def get_post_detail(post_id):
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post:
        return jsonify({"status": "error", "message": "Khong tim thay bai viet"}), 404
    return jsonify({"status": "success", "data": post}), 200

@app.route(f"{API_PREFIX}/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post:
        return jsonify({"status": "error", "message": "Khong tim thay bai viet"}), 404
    
    data = request.get_json() or {}
    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])
    return jsonify({"status": "success", "data": post}), 200

@app.route(f"{API_PREFIX}/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    global posts_db
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post:
        return jsonify({"status": "error", "message": "Khong tim thay bai viet"}), 404
    
    posts_db = [p for p in posts_db if p["id"] != post_id]
    return jsonify({"status": "success", "message": "Xoa bai viet thanh cong"}), 200

if __name__ == "__main__":
    app.run(debug=True)