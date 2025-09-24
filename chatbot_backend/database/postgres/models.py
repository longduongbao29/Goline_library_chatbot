"""
SQLAlchemy models for bookstore database
Includes Books and Orders tables with proper relationships
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class OrderStatus(enum.Enum):
    """Enum for order status"""
    PENDING = "pending"
    CONFIRMED = "confirmed" 
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Book(Base):
    """Books table model"""
    __tablename__ = 'books'
    
    book_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    category = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with orders
    orders = relationship("Order", back_populates="book")
    
    def __repr__(self):
        return f"<Book(id={self.book_id}, title='{self.title}', author='{self.author}', price={self.price})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Order(Base):
    """Orders table model"""
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(500), nullable=False)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    order_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with book
    book = relationship("Book", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.order_id}, customer='{self.customer_name}', book_id={self.book_id}, quantity={self.quantity})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'order_id': self.order_id,
            'customer_name': self.customer_name,
            'phone': self.phone,
            'address': self.address,
            'book_id': self.book_id,
            'quantity': self.quantity,
            'status': self.status.value if self.status else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'book': self.book.to_dict() if self.book else None
        }