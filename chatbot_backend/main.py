"""
FastAPI Chatbot Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

# Import API routes
from api.v1.completions import router as completions_router

# Import logger
from utils.logger import Logger

# Initialize logger
logger = Logger(__name__).get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Chatbot backend starting up...")
    logger.info("📚 Bookstore chatbot API is ready!")
    
    yield
    
    # Shutdown  
    logger.info("📴 Chatbot backend shutting down...")

# Create FastAPI application
app = FastAPI(
    title="Bookstore Chatbot API",
    description="API for bookstore chatbot with chat completions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(completions_router)

# Health check endpoint
@app.get("/health")
async def health():
    """Main health check endpoint"""
    return {
        "status": "healthy",
        "service": "chatbot-backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 1234))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
