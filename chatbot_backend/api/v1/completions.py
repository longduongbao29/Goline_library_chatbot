from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import time
from datetime import datetime

from utils.logger import Logger

router = APIRouter(prefix="/api/v1", tags=["completions"])
logger = Logger(__name__).get_logger()

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    text: str = Field(..., min_length=1, max_length=1000, description="User input text")
    user_id: Optional[str] = Field(None, description="Optional user identifier")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Chatbot response text")
    timestamp: str = Field(..., description="Response timestamp")
    processing_time: float = Field(..., description="Processing time in seconds")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    timestamp: str = Field(..., description="Error timestamp")

def process_chat_message(user_text: str, user_id: Optional[str] = None) -> str:
    """
    Process chat message and generate response
    
    Args:
        user_text: User input text
        user_id: Optional user identifier
        
    Returns:
        Generated response text
    """
    # Log the incoming request
    logger.info(f"Processing chat request from user {user_id or 'anonymous'}: {user_text[:50]}...")
    
    # Simple chatbot logic - replace this with your actual AI/LLM integration
    user_text_lower = user_text.lower().strip()
    
    # Simple rule-based responses for demonstration
    if "xin chào" in user_text_lower or "hello" in user_text_lower:
        response = "Xin chào! Tôi là chatbot của cửa hàng sách. Tôi có thể giúp bạn tìm kiếm sách, đặt hàng và trả lời các câu hỏi về sản phẩm. Bạn cần hỗ trợ gì?"
    
    elif "sách" in user_text_lower or "book" in user_text_lower:
        response = "Chúng tôi có nhiều loại sách: Lập trình, AI/ML, Database, Web Development, DevOps, và nhiều thể loại khác. Bạn muốn tìm sách về chủ đề nào?"
    
    elif "giá" in user_text_lower or "price" in user_text_lower or "bao nhiêu" in user_text_lower:
        response = "Giá sách của chúng tôi từ 200,000 - 600,000 VND tùy theo loại. Bạn có thể cho tôi biết tên sách cụ thể để tôi báo giá chính xác hơn không?"
    
    elif "đặt hàng" in user_text_lower or "mua" in user_text_lower or "order" in user_text_lower:
        response = "Để đặt hàng, bạn cần cung cấp: tên sách, số lượng, họ tên, số điện thoại và địa chỉ giao hàng. Tôi sẽ hỗ trợ bạn tạo đơn hàng."
    
    elif "python" in user_text_lower:
        response = "Chúng tôi có các sách về Python như: 'Lập trình Python cơ bản' (299,000 VND), 'Machine Learning với Python' (450,000 VND). Bạn quan tâm đến sách nào?"
    
    elif "cảm ơn" in user_text_lower or "thank" in user_text_lower:
        response = "Không có gì! Tôi rất vui được hỗ trợ bạn. Nếu bạn có thêm câu hỏi nào khác, đừng ngần ngại hỏi nhé!"
    
    elif "tạm biệt" in user_text_lower or "bye" in user_text_lower or "goodbye" in user_text_lower:
        response = "Tạm biệt! Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi. Chúc bạn một ngày tốt lành!"
    
    else:
        # Default response for unrecognized input
        response = f"Tôi hiểu bạn đang hỏi về '{user_text}'. Tôi có thể giúp bạn tìm kiếm sách, báo giá, hoặc hỗ trợ đặt hàng. Bạn có thể nói rõ hơn về nhu cầu của mình không?"
    
    logger.info(f"Generated response for user {user_id or 'anonymous'}: {response[:50]}...")
    return response

@router.post("/chat", response_model=ChatResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def chat(request: ChatRequest):
    """
    Chat with the chatbot
    
    - **text**: User input message (1-1000 characters)
    - **user_id**: Optional user identifier for tracking
    
    Returns chatbot response with processing metadata
    """
    start_time = time.time()
    
    try:
        logger.info(f"Chat API called with text length: {len(request.text)}")
        
        # Validate input
        if not request.text or not request.text.strip():
            logger.warning("Empty text received in chat request")
            raise HTTPException(
                status_code=400, 
                detail="Text input cannot be empty"
            )
        
        # Process the message
        response_text = process_chat_message(request.text, request.user_id)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create response
        response = ChatResponse(
            response=response_text,
            timestamp=datetime.now().isoformat(),
            processing_time=round(processing_time, 3)
        )
        
        logger.info(f"Chat request processed successfully in {processing_time:.3f}s")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while processing chat request"
        )