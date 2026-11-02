from factory import create_app
from api.extensions import db
from model.product import Product
from model.order import Order, OrderItem

app = create_app()

with app.app_context():
    # Kiểm tra nếu chưa có product nào thì mới tạo
    db.create_all()

    if not db.session.scalar(db.select(db.func.count()).select_from(Product)):
        p1 = Product(sku="PROD-101", name="Ban phim co", price_cents=1500000, qty_in_stock=10)
        p2 = Product(sku="PROD-102", name="Chuot khong dây", price_cents=800000, qty_in_stock=20)
        db.session.add_all([p1, p2])
        db.session.commit()

        # Tạo sẵn 1 đơn hàng chứa cả 2 sản phẩm trên
        order = Order(status="PENDING")
        item1 = OrderItem(product_id=p1.id, qty=1, price_cents=p1.price_cents)
        item2 = OrderItem(product_id=p2.id, qty=2, price_cents=p2.price_cents)
        order.items.extend([item1, item2])
        
        db.session.add(order)
        db.session.commit()
        print("=== SEED DATA SUCCESSFUL ===")