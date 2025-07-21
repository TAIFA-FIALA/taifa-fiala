from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn      

from app.core.config import settings
from app.core.database import create_tables
from app.api import api_router

# Create FastAPI application
app = FastAPI(
    title="AI Africa Funding Tracker",
    description="Comprehensive platform to track AI intelligence feed in Africa",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        print("🔄 Attempting to create database tables...")
        await create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Database table creation failed: {e}")
        print("⚠️ Application will continue without database tables")
        # Log the error but don't crash the application
        import logging
        logging.error(f"Database initialization failed: {e}", exc_info=True)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Africa Funding Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "ai-africa-funding-tracker",
        "version": "1.0.0"
    }

# Import our custom utilities
from app.utils.serialization import TaifaJsonEncoder, prepare_for_json
from app.utils.logging import log_api_error, logger, setup_file_logging
from app.utils.connection import connection_manager, shutdown_connection_manager

# Set up file-based logging
setup_file_logging()

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    # Log the exception with our enhanced logging
    log_api_error(
        error_type="http_exception",
        message=exc.detail,
        details={"status_code": exc.status_code},
        request=request
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": True}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    # Log the exception with our enhanced logging
    error_data = log_api_error(
        error_type="unhandled_exception",
        message=str(exc),
        request=request,
        exception=exc
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": True,
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        }
    )

@app.middleware("http")
async def serialize_response_middleware(request: Request, call_next):
    """Middleware to handle serialization of responses"""
    try:
        # Process the request and get response
        response = await call_next(request)
        return response
        
    except Exception as e:
        # If we encounter a serialization error, try to catch and fix it
        if isinstance(e, TypeError) and "not JSON serializable" in str(e):
            logger.error(f"JSON serialization error: {str(e)}")
            
            # Try to get the original response data
            if hasattr(e, "__context__") and hasattr(e.__context__, "obj"):
                # Try to serialize with our custom encoder
                try:
                    data = prepare_for_json(e.__context__.obj)
                    return JSONResponse(content=data)
                except Exception as inner_e:
                    logger.error(f"Failed to recover from serialization error: {str(inner_e)}")
        
        # Re-raise the exception for the general exception handler
        raise

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
