"""
Pinecone Client Initialization
==============================

This module provides a singleton instance of the Pinecone client
to be used across the application.
"""

import os
import logging
from typing import Union
from pinecone import Pinecone

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Pinecone client
try:
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        raise ValueError("PINECONE_API_KEY environment variable not set")
    
    pc = Pinecone(api_key=pinecone_api_key)
    logger.info("Successfully initialized Pinecone client")

except Exception as e:
    logger.error(f"Failed to initialize Pinecone client: {e}")
    pc = None

def get_pinecone_client() -> Union[Pinecone, None]:
    """
    Returns the singleton Pinecone client instance.
    """
    return pc