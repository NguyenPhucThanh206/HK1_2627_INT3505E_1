from flask import Flask
from api.extensions import db, migrate
from api.products import products_bp
from api.orders import orders_bp
from api.health import health_bp

def create_app():
    app = Flask(__name__)
    
    # Cấu hình chuỗi kết nối SQLite nội bộ để chạy test trực tiếp
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Khởi tạo extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Đăng ký Blueprints
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(health_bp)
    
    return app