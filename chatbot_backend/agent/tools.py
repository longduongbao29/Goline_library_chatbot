from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional, List, Dict, Any
import json
import sys
import os

from llm.llm_provider import get_chat_model
from agent.prompts import extract_info_prompt
from agent.structured_output import OrderInfo
from agent.utils import format_message
# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from database.postgres.repository import BookstoreRepository
from database.postgres.models import Book, Order, OrderStatus

from utils.logger import Logger
logger = Logger(__name__).get_logger()
# Global repository instance
_repo = None

def get_repository():
    """Get or create repository instance"""
    global _repo
    if _repo is None:
        _repo = BookstoreRepository()
    return _repo
repo = get_repository()
def search_book_func(
    title: Optional[str] = None,
    author: Optional[str] = None, 
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_stock: Optional[int] = None,
    max_results: Optional[int] = 10
):
    """
    Search for books in the bookstore database based on multiple criteria.
    
    Args:
        title: Book title (partial match supported)
        author: Author name (partial match supported)
        category: Book category/genre (partial match supported)
        min_price: Minimum price in VND
        max_price: Maximum price in VND  
        min_stock: Minimum stock quantity (default: only show books in stock)
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        JSON string with search results including book details
        
    Examples:
        - search_book(title="Python") - Find books with "Python" in title
        - search_book(author="Nguyễn") - Find books by authors with "Nguyễn" in name
        - search_book(category="lập trình", max_price=500000) - Programming books under 500k VND
        - search_book(min_price=200000, max_price=400000) - Books in price range 200k-400k VND
    """
    
    logger.debug("Search book")
    
    # Set default min_stock to 1 to only show available books
    if min_stock is None:
        min_stock = 1
    
    # Use repository search with filters
    if title or author or category:
        # Use search_books method for text search
        search_term = None
        if title:
            search_term = title
        elif author:
            search_term = author
        elif category:
            search_term = category
        
        books = repo.books.search_books(
            search_term=search_term,
            category=category if category and not search_term == category else None,
            min_price=min_price,
            max_price=max_price
        )
    else:
        # Get all books with pagination if no specific search term
        books = repo.books.get_all_books(limit=max_results)
    
    # Filter by stock and other criteria
    filtered_books = []
    for book in books:
        # Stock filter
        if book.stock < min_stock:
            continue
            
        # Additional title filter (case insensitive partial match)
        if title and title.lower() not in book.title.lower():
            continue
            
        # Additional author filter (case insensitive partial match)  
        if author and author.lower() not in book.author.lower():
            continue
            
        # Additional category filter (case insensitive partial match)
        if category and category.lower() not in book.category.lower():
            continue
        
        filtered_books.append(book)
    
    # Limit results
    if max_results and len(filtered_books) > max_results:
        filtered_books = filtered_books[:max_results]
    
    # Convert to response format
    if filtered_books:
        result = {
            "status": "success",
            "total_found": len(filtered_books),
            "books": []
        }
        
        for book in filtered_books:
            book_data = {
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "price": book.price,
                "stock": book.stock,
                "category": book.category,
                "availability": "In Stock" if book.stock > 0 else "Out of Stock"
            }
            result["books"].append(book_data)

        return result
    else:
        return None
@tool
def search_book(
    title: Optional[str] = None,
    author: Optional[str] = None, 
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_stock: Optional[int] = None,
    max_results: Optional[int] = 10
) -> str:
    """
    Search for books in the bookstore database based on multiple criteria.
    
    Args:
        title: Book title (partial match supported)
        author: Author name (partial match supported)
        category: Book category/genre (partial match supported)
        min_price: Minimum price in VND
        max_price: Maximum price in VND  
        min_stock: Minimum stock quantity (default: only show books in stock)
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        JSON string with search results including book details
        
    Examples:
        - search_book(title="Python") - Find books with "Python" in title
        - search_book(author="Nguyễn") - Find books by authors with "Nguyễn" in name
        - search_book(category="lập trình", max_price=500000) - Programming books under 500k VND
        - search_book(min_price=200000, max_price=400000) - Books in price range 200k-400k VND
    """
    try:
        logger.debug("Search book")
        
        # Set default min_stock to 1 to only show available books
        if min_stock is None:
            min_stock = 1
        
        # Use repository search with filters
        if title or author or category:
            # Use search_books method for text search
            search_term = None
            if title:
                search_term = title
            elif author:
                search_term = author
            elif category:
                search_term = category
            
            books = repo.books.search_books(
                search_term=search_term,
                category=category if category and not search_term == category else None,
                min_price=min_price,
                max_price=max_price
            )
        else:
            # Get all books with pagination if no specific search term
            books = repo.books.get_all_books(limit=max_results)
        
        # Filter by stock and other criteria
        filtered_books = []
        for book in books:
            # Stock filter
            if book.stock < min_stock:
                continue
                
            # Additional title filter (case insensitive partial match)
            if title and title.lower() not in book.title.lower():
                continue
                
            # Additional author filter (case insensitive partial match)  
            if author and author.lower() not in book.author.lower():
                continue
                
            # Additional category filter (case insensitive partial match)
            if category and category.lower() not in book.category.lower():
                continue
            
            filtered_books.append(book)
        
        # Limit results
        if max_results and len(filtered_books) > max_results:
            filtered_books = filtered_books[:max_results]
        
        # Convert to response format
        if filtered_books:
            result = {
                "status": "success",
                "total_found": len(filtered_books),
                "books": []
            }
            
            for book in filtered_books:
                book_data = {
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "price": book.price,
                    "stock": book.stock,
                    "category": book.category,
                    "availability": "In Stock" if book.stock > 0 else "Out of Stock"
                }
                result["books"].append(book_data)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        else:
            # No results found
            search_criteria = []
            if title:
                search_criteria.append(f"title containing '{title}'")
            if author:
                search_criteria.append(f"author containing '{author}'")
            if category:
                search_criteria.append(f"category containing '{category}'")
            if min_price:
                search_criteria.append(f"price >= {min_price:,} VND")
            if max_price:
                search_criteria.append(f"price <= {max_price:,} VND")
            if min_stock > 1:
                search_criteria.append(f"stock >= {min_stock}")
            
            criteria_text = " AND ".join(search_criteria) if search_criteria else "no specific criteria"
            
            result = {
                "status": "no_results",
                "message": f"No books found matching: {criteria_text}",
                "suggestions": [
                    "Try broader search terms",
                    "Check spelling of title/author names", 
                    "Remove some filters to see more results",
                    "Browse available categories: Lập trình, AI/ML, Database, Web Development, etc."
                ]
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
    except Exception as e:
        # Error handling
        error_result = {
            "status": "error",
            "message": f"Database error occurred: {str(e)}",
            "error_type": type(e).__name__
        }
        
        return json.dumps(error_result, ensure_ascii=False, indent=2)
def get_follow_up_question(info):
    dict_ = {
        "customer_name": "Tên đầy đủ của bạn là gì?",
        "phone": "Số điện thoại của bạn là gì?",
        "address": "Địa chỉ giao hàng của bạn là gì?",
        "book_title": "Bạn muốn đặt sách nào?",
        "quantity": "Bạn muốn đặt bao nhiêu cuốn?"
    }
    if info in dict_:
        return dict_[info]
    else:
        return "Bạn vui lòng cung cấp thêm thông tin chi tiết."
@tool 
def order_book(
    customer_name: str = None, 
    phone: str = None, 
    address: str = None, 
    book_title: str = None, 
    quantity: int = None
) -> str:
    """
    Create a new order for a customer to purchase books.
    
    Args:
        customer_name: Full name of the customer
        phone: Customer's phone number (Vietnamese format, e.g., 0901234567)
        address: Full delivery address including street, district, city
        book_title: Title of the book to order (get from search_book results)
        quantity: Number of books to order (default: 1)

    Returns:
        JSON string with order confirmation details or error information
        
    """
    state = {
        "customer_name": customer_name,
        "phone": phone,
        "address": address,
        "book_title": book_title,
        "quantity": quantity ,
        "book_id": None,
        "author": None,
        "price": None,
        "category": None,
    }
    if book_title:
        # Search for the book by title
        search_result_json = search_book(title=book_title, max_results=1)
        search_result = json.loads(search_result_json)
        
        if search_result.get("status") == "success" and search_result.get("books"):
            book_info = search_result["books"][0]
            state["book_id"] = book_info["book_id"]
            state["author"] = book_info["author"]
            state["price"] = book_info["price"]
            state["category"] = book_info["category"]
        else:
            return json.dumps({
                "status": "error",
                "message": f"Không tìm thấy sách với tiêu đề '{book_title}'. Vui lòng kiểm tra lại tên sách."
            }, ensure_ascii=False, indent=2)
    
def create_order(customer_name: str, phone: str, address: str, book_id: int, quantity: int = 1) -> str:
    """
    Create a new order for a customer to purchase books.
    
    Args:
        customer_name: Full name of the customer
        phone: Customer's phone number (Vietnamese format, e.g., 0901234567)
        address: Full delivery address including street, district, city
        book_id: ID of the book to order (get from search_book results)
        quantity: Number of books to order (default: 1)
        
    Returns:
        JSON string with order confirmation details or error information
        
    Examples:
        - create_order("Nguyễn Văn A", "0901234567", "123 Lê Lợi, Q1, TP.HCM", 1, 2)
        - create_order("Trần Thị B", "0987654321", "456 Nguyễn Huệ, Q3, TP.HCM", 5, 1)
    """
    try:
   
        
        # Validate input
        if not customer_name or not customer_name.strip():
            return json.dumps({
                "status": "error",
                "message": "Tên khách hàng không được để trống"
            }, ensure_ascii=False, indent=2)
        
        if not phone or not phone.strip():
            return json.dumps({
                "status": "error", 
                "message": "Số điện thoại không được để trống"
            }, ensure_ascii=False, indent=2)
        
        if not address or not address.strip():
            return json.dumps({
                "status": "error",
                "message": "Địa chỉ giao hàng không được để trống"
            }, ensure_ascii=False, indent=2)
        
        if quantity <= 0:
            return json.dumps({
                "status": "error",
                "message": "Số lượng sách phải lớn hơn 0"
            }, ensure_ascii=False, indent=2)
        
        # Check if book exists and has enough stock
        book = repo.books.get_book_by_id(book_id)
        if not book:
            return json.dumps({
                "status": "error",
                "message": f"Không tìm thấy sách với ID {book_id}. Vui lòng kiểm tra lại thông tin sách."
            }, ensure_ascii=False, indent=2)
        
        if book.stock < quantity:
            return json.dumps({
                "status": "error",
                "message": f"Không đủ hàng tồn kho. Hiện tại chỉ còn {book.stock} cuốn '{book.title}', bạn đang yêu cầu {quantity} cuốn."
            }, ensure_ascii=False, indent=2)
        
        # Create the order
        order = repo.orders.create_order(
            customer_name=customer_name.strip(),
            phone=phone.strip(),
            address=address.strip(),
            book_id=book_id,
            quantity=quantity
        )
        
        if order:
            total_amount = book.price * quantity
            
            result = {
                "status": "success",
                "message": "Đặt hàng thành công!",
                "order_details": {
                    "order_id": order.order_id,
                    "customer_name": order.customer_name,
                    "phone": order.phone,
                    "address": order.address,
                    "book": {
                        "book_id": book.book_id,
                        "title": book.title,
                        "author": book.author,
                        "price": book.price
                    },
                    "quantity": quantity,
                    "total_amount": total_amount,
                    "status": "Đang chờ xử lý",
                    "order_date": order.order_date.strftime("%d/%m/%Y %H:%M:%S") if order.order_date else None
                },
                "next_steps": [
                    "Chúng tôi sẽ liên hệ với bạn trong vòng 24h để xác nhận đơn hàng",
                    "Thời gian giao hàng dự kiến: 2-3 ngày làm việc", 
                    "Bạn có thể thanh toán khi nhận hàng (COD)"
                ]
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "status": "error",
                "message": "Có lỗi xảy ra khi tạo đơn hàng. Vui lòng thử lại sau."
            }, ensure_ascii=False, indent=2)
            
    except Exception as e:
        error_result = {
            "status": "error", 
            "message": f"Lỗi hệ thống khi tạo đơn hàng: {str(e)}"
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

