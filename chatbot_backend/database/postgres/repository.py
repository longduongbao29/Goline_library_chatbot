"""
Repository pattern for database operations
Provides high-level methods for CRUD operations on Books and Orders
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from database.postgres.models import Book, Order, OrderStatus
from database.postgres.PostgresDB import PostgresDB

from utils.logger import Logger
logger = Logger(__name__).get_logger()

class BookRepository:
    """Repository for Book operations"""
    
    def __init__(self, db: PostgresDB):
        self.db = db
    
    def create_book(self, title: str, author: str, price: float, stock: int, category: str) -> Optional[Book]:
        """Create a new book"""
        try:
            with self.db.get_session() as session:
                book = Book(
                    title=title,
                    author=author,
                    price=price,
                    stock=stock,
                    category=category
                )
                session.add(book)
                session.flush()
                return book
        except Exception as e:
            logger.error(f"Failed to create book: {e}")
            return None
    
    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Get book by ID"""
        try:
            with self.db.get_session() as session:
                return session.query(Book).filter(Book.book_id == book_id).first()
        except Exception as e:
            logger.error(f"Failed to get book by ID {book_id}: {e}")
            return None
    
    def get_all_books(self, limit: int = None, offset: int = 0) -> List[Book]:
        """Get all books with optional pagination"""
        try:
            with self.db.get_session() as session:
                query = session.query(Book).order_by(Book.book_id)
                if limit:
                    query = query.limit(limit).offset(offset)
                return query.all()
        except Exception as e:
            logger.error(f"Failed to get all books: {e}")
            return []
    
    def search_books(self, search_term: str = None, category: str = None, 
                    min_price: float = None, max_price: float = None) -> List[Book]:
        """Search books with filters"""
        try:
            with self.db.get_session() as session:
                query = session.query(Book)
                
                conditions = []
                
                if search_term:
                    search_pattern = f"%{search_term}%"
                    conditions.append(
                        or_(
                            Book.title.ilike(search_pattern),
                            Book.author.ilike(search_pattern)
                        )
                    )
                
                if category:
                    conditions.append(Book.category.ilike(f"%{category}%"))
                
                if min_price is not None:
                    conditions.append(Book.price >= min_price)
                
                if max_price is not None:
                    conditions.append(Book.price <= max_price)
                
                if conditions:
                    query = query.filter(and_(*conditions))
                
                return query.order_by(Book.title).all()
        except Exception as e:
            logger.error(f"Failed to search books: {e}")
            return []
    
    def update_book_stock(self, book_id: int, new_stock: int) -> bool:
        """Update book stock"""
        try:
            with self.db.get_session() as session:
                book = session.query(Book).filter(Book.book_id == book_id).first()
                if book:
                    book.stock = new_stock
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to update book stock: {e}")
            return False
    
    def reduce_stock(self, book_id: int, quantity: int) -> bool:
        """Reduce book stock (for orders)"""
        try:
            with self.db.get_session() as session:
                book = session.query(Book).filter(Book.book_id == book_id).first()
                if book and book.stock >= quantity:
                    book.stock -= quantity
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to reduce book stock: {e}")
            return False
    
    def delete_book(self, book_id: int) -> bool:
        """Delete a book (soft delete by setting stock to 0)"""
        try:
            with self.db.get_session() as session:
                book = session.query(Book).filter(Book.book_id == book_id).first()
                if book:
                    book.stock = 0
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to delete book: {e}")
            return False

class OrderRepository:
    """Repository for Order operations"""
    
    def __init__(self, db: PostgresDB):
        self.db = db
    
    def create_order(self, customer_name: str, phone: str, address: str, 
                    book_id: int, quantity: int) -> Optional[Order]:
        """Create a new order"""
        try:
            with self.db.get_session() as session:
                # Get book to calculate total amount
                book = session.query(Book).filter(Book.book_id == book_id).first()
                if not book:
                    logger.error(f"Book with ID {book_id} not found")
                    return None
                
                if book.stock < quantity:
                    logger.error(f"Insufficient stock. Available: {book.stock}, Requested: {quantity}")
                    return None
                
                total_amount = book.price * quantity
                
                order = Order(
                    customer_name=customer_name,
                    phone=phone,
                    address=address,
                    book_id=book_id,
                    quantity=quantity,
                    total_amount=total_amount,
                    status=OrderStatus.PENDING
                )
                
                session.add(order)
                
                # Reduce book stock
                book.stock -= quantity
                
                session.flush()
                return order
                
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            return None
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID with book details"""
        try:
            with self.db.get_session() as session:
                return session.query(Order).filter(Order.order_id == order_id).first()
        except Exception as e:
            logger.error(f"Failed to get order by ID {order_id}: {e}")
            return None
    
    def get_orders_by_customer(self, customer_name: str = None, phone: str = None) -> List[Order]:
        """Get orders by customer name or phone"""
        try:
            with self.db.get_session() as session:
                query = session.query(Order)
                
                if customer_name:
                    query = query.filter(Order.customer_name.ilike(f"%{customer_name}%"))
                if phone:
                    query = query.filter(Order.phone == phone)
                
                return query.order_by(desc(Order.order_date)).all()
        except Exception as e:
            logger.error(f"Failed to get orders by customer: {e}")
            return []
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get orders by status"""
        try:
            with self.db.get_session() as session:
                return session.query(Order).filter(Order.status == status).order_by(desc(Order.order_date)).all()
        except Exception as e:
            logger.error(f"Failed to get orders by status: {e}")
            return []
    
    def update_order_status(self, order_id: int, new_status: OrderStatus) -> bool:
        """Update order status"""
        try:
            with self.db.get_session() as session:
                order = session.query(Order).filter(Order.order_id == order_id).first()
                if order:
                    old_status = order.status
                    order.status = new_status
                    
                    # If cancelling order, restore book stock
                    if new_status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
                        book = session.query(Book).filter(Book.book_id == order.book_id).first()
                        if book:
                            book.stock += order.quantity
                    
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to update order status: {e}")
            return False
    
    def get_order_statistics(self) -> Dict[str, Any]:
        """Get order statistics"""
        try:
            with self.db.get_session() as session:
                total_orders = session.query(Order).count()
                total_revenue = session.query(Order).filter(
                    Order.status != OrderStatus.CANCELLED
                ).with_entities(
                    session.query(Order.total_amount).label('total')
                ).scalar() or 0
                
                status_counts = {}
                for status in OrderStatus:
                    count = session.query(Order).filter(Order.status == status).count()
                    status_counts[status.value] = count
                
                return {
                    'total_orders': total_orders,
                    'total_revenue': total_revenue,
                    'status_breakdown': status_counts
                }
        except Exception as e:
            logger.error(f"Failed to get order statistics: {e}")
            return {}

class BookstoreRepository:
    """Main repository combining both Book and Order operations"""
    
    def __init__(self, database_url: str = None):
        self.db = PostgresDB(database_url=database_url)
        self.db.connect()
        
        self.books = BookRepository(self.db)
        self.orders = OrderRepository(self.db)
    
    def close(self):
        """Close database connection"""
        self.db.close_connection()