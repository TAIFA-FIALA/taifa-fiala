"""
TAIFA-FIALA API Logging Utilities
Provides enhanced logging capabilities for better error tracking and debugging
"""

import logging
import traceback
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import Request
from starlette.responses import Response

# Import our custom JSON serializer to handle complex types in logs
from app.utils.serialization import prepare_for_json

# Configure base logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create logger
logger = logging.getLogger("taifa-api")


def get_request_details(request: Request) -> Dict[str, Any]:
    """Extract useful details from a request for logging purposes"""
    client_host = request.client.host if request.client else "unknown"
    return {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "client_ip": client_host,
        "headers": dict(request.headers),
        "timestamp": datetime.now().isoformat()
    }


def setup_request_logging():
    """Set up middleware for request logging"""
    from fastapi import FastAPI
    
    app = FastAPI()  # This is just a placeholder, will be replaced with the actual app
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log requests and responses with timing information"""
        request_id = request.headers.get("X-Request-ID", "unknown")
        start_time = datetime.now()
        
        # Log request details
        request_details = get_request_details(request)
        logger.info(f"Request {request_id} started: {json.dumps(request_details)}")
        
        try:
            # Process the request and get the response
            response = await call_next(request)
            
            # Calculate processing time
            process_time = (datetime.now() - start_time).total_seconds()
            
            # Log response details
            logger.info(
                f"Request {request_id} completed in {process_time:.3f}s with status {response.status_code}"
            )
            
            return response
            
        except Exception as e:
            # Log any uncaught exceptions
            process_time = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"Request {request_id} failed after {process_time:.3f}s: {str(e)}\n"
                f"Path: {request.url.path}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            raise
    
    return log_requests


def log_api_error(
    error_type: str,
    message: str, 
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
    exception: Optional[Exception] = None
):
    """
    Enhanced error logging with context details
    
    Args:
        error_type: Type/category of error (e.g., 'validation', 'database', 'serialization')
        message: Main error message
        details: Additional context for the error
        request: FastAPI request object if available
        exception: Exception object if available
    """
    error_data = {
        "type": error_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
    
    if details:
        try:
            # Use our custom JSON preparation to handle complex types
            error_data["details"] = prepare_for_json(details)
        except Exception as e:
            error_data["details"] = str(details)
            error_data["details_serialization_error"] = str(e)
    
    if request:
        error_data["request"] = get_request_details(request)
    
    if exception:
        error_data["exception"] = {
            "type": type(exception).__name__,
            "message": str(exception),
            "traceback": traceback.format_exception(type(exception), exception, exception.__traceback__)
        }
    
    log_message = f"API ERROR [{error_type}]: {message}"
    logger.error(log_message)
    logger.debug(json.dumps(error_data, indent=2))
    
    return error_data


# Setup file-based logging if needed
def setup_file_logging(log_dir: str = "logs"):
    """Setup additional file-based logging"""
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create file handler for error logs
    error_handler = logging.FileHandler(log_path / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)
    
    # Create file handler for all logs
    all_handler = logging.FileHandler(log_path / "all.log")
    all_handler.setLevel(logging.INFO)
    all_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    all_handler.setFormatter(all_formatter)
    
    # Add handlers to logger
    logger.addHandler(error_handler)
    logger.addHandler(all_handler)
