"""
TAIFA-FIALA Connection Management Utilities
Provides improved connection handling with retry logic for API stability
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
import aiohttp
import backoff
import time
from functools import wraps

# Import our custom logging utility
from app.utils.logging import logger

# Type variable for return types
T = TypeVar('T')


class ConnectionManager:
    """
    Manages HTTP connections with retry logic, timeouts, and connection pooling
    for improved API stability and reliability.
    """
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        max_connections: int = 100
    ):
        """
        Initialize connection manager
        
        Args:
            timeout: Default timeout for requests in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff multiplier
            max_connections: Maximum number of connections in the pool
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_connections = max_connections
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def get_session(self) -> aiohttp.ClientSession:
        """
        Get or create an aiohttp session with proper connection pooling
        
        Returns:
            An aiohttp client session
        """
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                ttl_dns_cache=300,  # Cache DNS results for 5 minutes
                force_close=False,  # Keep connections alive when possible
            )
            
            # Create session with proper timeout and connection settings
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                raise_for_status=False,  # We'll handle status codes manually
            )
            
        return self.session
    
    async def close(self) -> None:
        """Close the session if it exists"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        factor=1.5
    )
    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Make an HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            **kwargs: Additional arguments to pass to the request method
            
        Returns:
            aiohttp ClientResponse object
        """
        session = await self.get_session()
        
        # Set default timeout if not specified
        timeout = kwargs.pop('timeout', self.timeout)
        if timeout is not None:
            kwargs['timeout'] = aiohttp.ClientTimeout(total=timeout)
        
        try:
            start_time = time.time()
            response = await session.request(method, url, **kwargs)
            duration = time.time() - start_time
            
            # Log request details
            logger.info(
                f"{method} {url} completed in {duration:.3f}s with status {response.status}"
            )
            
            return response
            
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Connection error during {method} {url}: {str(e)}")
            raise
    
    
# Create a global instance for use throughout the application
connection_manager = ConnectionManager()


# Decorator for retry logic on any function
def with_retry(
    max_tries: int = 3,
    backoff_factor: float = 1.5,
    retry_on_exceptions: tuple = (Exception,),
    logger_func: Optional[Callable] = None
):
    """
    Decorator for adding retry logic to any function
    
    Args:
        max_tries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        retry_on_exceptions: Tuple of exceptions that trigger retries
        logger_func: Optional function to call for logging retries
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None
            
            while attempt < max_tries:
                try:
                    return await func(*args, **kwargs)
                except retry_on_exceptions as e:
                    attempt += 1
                    last_exception = e
                    
                    # Calculate sleep time with exponential backoff
                    sleep_time = backoff_factor * (2 ** (attempt - 1))
                    
                    # Log retry attempt
                    if logger_func:
                        logger_func(
                            f"Retry {attempt}/{max_tries} for {func.__name__} "
                            f"after error: {str(e)}. Waiting {sleep_time:.2f}s"
                        )
                    else:
                        logger.warning(
                            f"Retry {attempt}/{max_tries} for {func.__name__} "
                            f"after error: {str(e)}. Waiting {sleep_time:.2f}s"
                        )
                    
                    # Sleep before retry
                    if attempt < max_tries:
                        await asyncio.sleep(sleep_time)
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    
    return decorator


# Application shutdown handler
async def shutdown_connection_manager():
    """Close connections when application shuts down"""
    await connection_manager.close()
    logger.info("Connection manager shut down successfully")
