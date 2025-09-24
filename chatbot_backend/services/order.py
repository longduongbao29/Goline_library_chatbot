
import json
from database.postgres.repository import get_repository

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
        # Get repository instance
        repo = get_repository()
   
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
                    "total_amount": book.price * quantity,
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

