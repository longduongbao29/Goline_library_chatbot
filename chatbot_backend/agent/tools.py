from langchain_core.tools import tool
from typing import Optional
import json
import sys
import os

from database.postgres.repository import get_repository
# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.logger import Logger
logger = Logger(__name__).get_logger()
# Global repository instance


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
        category_filter = None
        
        if title:
            search_term = title
        elif author:
            search_term = author
        
        # Category is handled separately to avoid confusion
        if category:
            category_filter = category
        
        books = repo.books.search_books(
            search_term=search_term,
            category=category_filter,
            min_price=min_price,
            max_price=max_price
        )
    else:
        # Get all books with pagination if no specific search term
        books = repo.books.get_all_books(limit=max_results)
    
    # Filter by stock only (other filters already handled by repository)
    filtered_books = []
    for book in books:
        # Stock filter - only filter that needs to be applied here
        if book.stock < min_stock:
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
            category_filter = None
            
            if title:
                search_term = title
            elif author:
                search_term = author
            
            # Category is handled separately to avoid confusion
            if category:
                category_filter = category
            
            books = repo.books.search_books(
                search_term=search_term,
                category=category_filter,
                min_price=min_price,
                max_price=max_price
            )
        else:
            # Get all books with pagination if no specific search term
            books = repo.books.get_all_books(limit=max_results)
        
        # Filter by stock only (other filters already handled by repository)
        filtered_books = []
        for book in books:
            # Stock filter - only filter that needs to be applied here
            if book.stock < min_stock:
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
