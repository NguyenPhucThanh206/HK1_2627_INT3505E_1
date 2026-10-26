from datetime import datetime, timezone, timedelta
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

# Giả lập Database trong bộ nhớ với tên mới
MOCK_USERS = {
    "nguyenhi@gmail.com": {
        "id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
        "email": "nguyenhi@gmail.com",
        "username": "Nguyen_Van_A",
        "display_name": "Nguyễn Hi",
        "password": "Password123@",
        "avatar_url": "https://cdn.socialnetwork.vn/avatars/Nguyen_Van_A.png",
        "role": "USER",
        "is_active": True,
        "phone_number": "+84912115199",
        "password_hash": "$2b$12$e8k9J9M9...", 
    }
}

MOCK_POSTS = {
    "123e4567-e89b-12d3-a456-426614174000": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "authorId": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
        "content": "Bài viết thử nghiệm trên Social Network API!",
        "createdAt": "2026-10-26T08:00:00Z"
    }
}

VALID_REFRESH_TOKENS = {"mock-refresh-token-xyz"}

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Bad Request", "message": "Thiếu email hoặc password"}), 400

    email = data['email']
    password = data['password']

    user = MOCK_USERS.get(email)
    if not user or user['password'] != password:
        return jsonify({"error": "Unauthorized", "message": "Sai email hoặc mật khẩu"}), 401

    return jsonify({
        "accessToken": f"mock-access-token-for-{user['id']}",
        "refreshToken": "mock-refresh-token-xyz"
    }), 200

@app.route('/api/v1/auth/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    if not data or not data.get('refreshToken'):
        return jsonify({"error": "Bad Request", "message": "Thiếu refreshToken"}), 400

    refresh_token = data['refreshToken']
    if refresh_token not in VALID_REFRESH_TOKENS:
        return jsonify({"error": "Unauthorized", "message": "Refresh token không hợp lệ hoặc đã hết hạn"}), 401

    return jsonify({
        "accessToken": f"new-mock-access-token-{int(time.time())}"
    }), 200

@app.route('/api/v1/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized", "message": "Yêu cầu Bearer token"}), 401

    post = MOCK_POSTS.get(post_id)
    if not post:
        return jsonify({"error": "Not Found", "message": "Không tìm thấy bài viết"}), 404

    return jsonify(post), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)