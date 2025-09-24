from pydantic import BaseModel, Field
from typing import Literal, Optional

class OrderInfo(BaseModel):
    book_title: Optional[str] = Field(None, description="Tên sách nếu có")
    quantity: int = Field(1, description="Số lượng sách")
    customer_name: Optional[str] = Field(None, description="Tên khách hàng nếu có")
    phone: Optional[str] = Field(None, description="Số điện thoại nếu có")
    address: Optional[str] = Field(None, description="Địa chỉ giao hàng nếu có")

class IntentDetection(BaseModel):
    intent: Literal["order_book", "search_book", "unknown"] = Field(..., description="Detected user intent")
class OrderIntent(BaseModel):
    action: Literal["search", "collect", "update"] = Field(..., description="Action to take based on order info and conversation")