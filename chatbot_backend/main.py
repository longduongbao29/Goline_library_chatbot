from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from api.v1.completions import router as completions_router
from utils.logger import Logger
from config.configures import config

logger = Logger(__name__).get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Chatbot backend starting up...")
    logger.info("Bookstore chatbot API is ready!")
    
    yield
    
    # Shutdown  
    logger.info("Chatbot backend shutting down...")

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
    allow_origins=["*"],  
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
    # Get configuration from config class
    logger.info("Loading configuration...")
    
    logger.info(f"Starting server on {config.server.host}:{config.server.port}")
    
    uvicorn.run(
        "main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
        log_level=config.server.log_level
    )
