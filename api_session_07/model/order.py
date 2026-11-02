from typing import List
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.extensions import db

class Order(db.Model):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    createed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(),nullable=False)

    items: Mapped[List["OrderItem"]] = relationship(back_populates="order")

class OrderItem(db.Model):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)

    price_cents: Mapped[int] = mapped_column(Integer, nullable=False) 
    
    order: Mapped["Order"] = relationship(back_populates="items")