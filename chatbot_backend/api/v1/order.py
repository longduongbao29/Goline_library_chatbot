from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
import json
from typing import Optional
from utils.logger import Logger

# Import services
from services.order import create_order
from database.postgres.repository import get_repository

logger = Logger(__name__).get_logger()

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderConfirmationRequest(BaseModel):
    """Request model for order confirmation from UI card"""
    book_id: int = Field(..., description="ID of the book to order")
    book_title: str = Field(..., description="Title of the book")
    author: Optional[str] = Field(None, description="Author of the book")
    category: Optional[str] = Field(None, description="Category of the book")
    quantity: int = Field(default=1, ge=1, description="Quantity to order (minimum 1)")
    customer_name: str = Field(..., min_length=1, description="Customer full name")
    phone: str = Field(..., min_length=10, description="Customer phone number")
    address: str = Field(..., min_length=5, description="Delivery address")

    @validator('phone')
    def validate_phone(cls, v):
        # Remove spaces and special characters
        cleaned = ''.join(filter(str.isdigit, v))
        
        # Check Vietnamese phone format
        if len(cleaned) not in [10, 11]:
            raise ValueError('Số điện thoại không hợp lệ. Vui lòng nhập đúng định dạng Việt Nam (10-11 số)')
        
        if not (cleaned.startswith('0') or cleaned.startswith('84')):
            raise ValueError('Số điện thoại phải bắt đầu bằng 0 hoặc 84')
            
        return cleaned

    @validator('customer_name')
    def validate_customer_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Tên khách hàng không được để trống')
        return v.strip()

    @validator('address')
    def validate_address(cls, v):
        if not v or not v.strip():
            raise ValueError('Địa chỉ giao hàng không được để trống')
        return v.strip()

class OrderResponse(BaseModel):
    """Response model for order operations"""
    success: bool
    message: str
    order_id: Optional[int] = None
    order_details: Optional[dict] = None


@router.post("/confirm", response_model=OrderResponse, summary="Confirm Order from UI Card")
async def confirm_order(request: OrderConfirmationRequest):
    """
    Confirm and create order from UI confirmation card.
    
    This endpoint receives order data from the confirmation card in the chat UI
    and creates the order in the database.
    
    Args:
        request: Order confirmation data from UI card
        
    Returns:
        OrderResponse with success status and order details
        
    Raises:
        HTTPException: If validation fails or order creation encounters errors
    """
    try:
        logger.info(f"Received order confirmation request: {request.dict()}")
        
        # Call the order service to create the order
        result_json = create_order(
            customer_name=request.customer_name,
            phone=request.phone,
            address=request.address,
            book_id=request.book_id,
            quantity=request.quantity
        )
        
        # Parse the JSON result from service
        result = json.loads(result_json)
        
        if result.get("status") == "success":
            logger.info(f"Order created successfully: {result.get('order_details', {}).get('order_id')}")
            
            return OrderResponse(
                success=True,
                message=result.get("message", "Đặt hàng thành công!"),
                order_id=result.get("order_details", {}).get("order_id"),
                order_details=result.get("order_details")
            )
        else:
            logger.warning(f"Order creation failed: {result.get('message')}")
            
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "message": result.get("message", "Đặt hàng thất bại"),
                    "error_type": "order_creation_failed"
                }
            )
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse order service response: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Lỗi hệ thống khi xử lý đơn hàng",
                "error_type": "json_parse_error"
            }
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "message": str(e),
                "error_type": "validation_error"
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in order confirmation: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Đã có lỗi không mong muốn xảy ra. Vui lòng thử lại sau.",
                "error_type": "internal_server_error"
            }
        )


@router.get("/status/{order_id}", summary="Get Order Status")
async def get_order_status(order_id: int):
    """
    Get order status by order ID.
    
    Args:
        order_id: The ID of the order to check
        
    Returns:
        Order status and details
    """
    try:
        repo = get_repository()
        order = repo.orders.get_order_by_id(order_id)
        
        if not order:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "message": f"Không tìm thấy đơn hàng với ID {order_id}",
                    "error_type": "order_not_found"
                }
            )
        
        # Get book details
        book = repo.books.get_book_by_id(order.book_id)
        
        order_details = {
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "phone": order.phone,
            "address": order.address,
            "book": {
                "book_id": book.book_id if book else None,
                "title": book.title if book else "N/A",
                "author": book.author if book else "N/A",
                "price": book.price if book else 0
            },
            "quantity": order.quantity,
            "total_amount": (book.price * order.quantity) if book else 0,
            "status": order.status,
            "order_date": order.order_date.strftime("%d/%m/%Y %H:%M:%S") if order.order_date else None
        }
        
        return {
            "success": True,
            "message": "Lấy thông tin đơn hàng thành công",
            "order_details": order_details
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order status: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Lỗi hệ thống khi lấy thông tin đơn hàng",
                "error_type": "internal_server_error"
            }
        )


@router.get("/list", summary="List Customer Orders")
async def list_orders(customer_phone: Optional[str] = None, limit: int = 10):
    """
    List orders, optionally filtered by customer phone.
    
    Args:
        customer_phone: Filter by customer phone number
        limit: Maximum number of orders to return
        
    Returns:
        List of orders
    """
    try:
        # This would need to be implemented in the repository layer
        # orders = repo.orders.list_orders(customer_phone=customer_phone, limit=limit)
        
        return {
            "success": True,
            "message": "Lấy danh sách đơn hàng thành công",
            "orders": [],  # Placeholder - implement in repository
            "total": 0
        }
        
    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Lỗi hệ thống khi lấy danh sách đơn hàng",
                "error_type": "internal_server_error"
            }
        )
