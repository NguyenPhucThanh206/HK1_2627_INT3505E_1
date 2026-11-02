from flask import Blueprint, jsonify, request
from .extensions import db
from model.order import Order, OrderItem
from model.product import Product
from model.schemas import OrderIn, OrderOut
from .errors import OutOfStock, NotFound
from sqlalchemy.orm import joinedload

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")

@orders_bp.post("")
def create_order():
    body = OrderIn().load(request.json)
    
    # Tạo đơn hàng mới
    new_order = Order(status="pending")
    db.session.add(new_order)
    
    for item in body["items"]:
        # Tìm sản phẩm, nếu đã xóa mềm thì báo lỗi
        product = db.get_or_404(Product, item["product_id"])
        if product.archived:
            raise NotFound(message=f"Sản phẩm {item['product_id']} không tồn tại")
            
        # Kiểm tra tồn kho
        if product.qty_in_stock < item["qty"]:
            raise OutOfStock(message=f"Sản phẩm {product.id} chỉ còn {product.qty_in_stock} sản phẩm")
            
        # Trừ tồn kho
        product.qty_in_stock -= item["qty"]
        
        # Tạo OrderItem ghi nhận giá tại thời điểm hiện tại
        order_item = OrderItem(
            order=new_order,
            product_id=product.id,
            qty=item["qty"],
            price_cents=product.price_cents
        )
        db.session.add(order_item)
        
    # Commit toàn bộ thay đổi (Order, OrderItems, trừ Product qty) trong 1 transaction
    db.session.commit()
    return OrderOut().dump(new_order), 201

@orders_bp.get("")
def list_orders():
    # Sử dụng joinedload để load Order và OrderItems trong 1 query duy nhất
    orders = db.session.execute(
        db.select(Order).options(joinedload(Order.items))
    ).scalars().unique().all()
    return jsonify({"items": [OrderOut().dump(o) for o in orders]}), 200