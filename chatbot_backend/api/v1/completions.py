from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import time
from datetime import datetime

from agent.langgraph import Agent

from utils.logger import Logger

router = APIRouter(prefix="/api/v1", tags=["completions"])
logger = Logger(__name__).get_logger()
agent = Agent()
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
    response = agent.run(user_text, user_id=user_id)
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