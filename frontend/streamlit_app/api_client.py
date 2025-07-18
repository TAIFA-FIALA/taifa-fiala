"""
TAIFA-FIALA API Client
Handles communication between Streamlit frontend and FastAPI backend
"""

import aiohttp
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import streamlit as st
import os

logger = logging.getLogger(__name__)

class TaifaAPIClient:
    """API client for TAIFA-FIALA backend"""
    
    def __init__(self, base_url: str = os.getenv("TAIFA_API_BASE_URL", "http://localhost:8000/api/v1")):
        self.base_url = base_url
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_africa_intelligence_feed(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get intelligence feed with filters"""
        try:
            session = await self._get_session()
            
            params = {"skip": skip, "limit": limit}
            if status:
                params["status"] = status
            if min_amount:
                params["min_amount"] = min_amount
            if max_amount:
                params["max_amount"] = max_amount
            
            url = f"{self.base_url}/funding-opportunities/"
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API error {response.status}: {await response.text()}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching opportunities: {e}")
            return []
    
    async def search_africa_intelligence_feed(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search intelligence feed"""
        try:
            session = await self._get_session()
            
            params = {"q": query, "limit": limit}
            url = f"{self.base_url}/funding-opportunities/search/"
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Search API error {response.status}: {await response.text()}")
                    return []
        except Exception as e:
            logger.error(f"Error searching opportunities: {e}")
            return []
    
    async def create_intelligence_item(self, opportunity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new intelligence item"""
        try:
            session = await self._get_session()
            
            url = f"{self.base_url}/funding-opportunities/"
            async with session.post(url, json=opportunity_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Create API error {response.status}: {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Error creating opportunity: {e}")
            return None
    
    async def get_opportunity_by_id(self, opportunity_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific opportunity by ID"""
        try:
            session = await self._get_session()
            
            url = f"{self.base_url}/funding-opportunities/{opportunity_id}"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    logger.error(f"API error {response.status}: {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching opportunity {opportunity_id}: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if the API is healthy"""
        try:
            session = await self._get_session()
            
            url = f"{self.base_url.replace('/api/v1', '')}/health"
            async with session.get(url) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

# Streamlit-specific helpers
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_opportunities_sync(skip: int = 0, limit: int = 100, **filters):
    """Synchronous wrapper for Streamlit"""
    client = TaifaAPIClient()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.get_africa_intelligence_feed(skip, limit, **filters))
        loop.run_until_complete(client.close())
        return result
    finally:
        loop.close()

@st.cache_data(ttl=60)  # Cache for 1 minute
def search_opportunities_sync(query: str, limit: int = 10):
    """Synchronous search wrapper for Streamlit"""
    if not query.strip():
        return []
    
    client = TaifaAPIClient()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.search_africa_intelligence_feed(query, limit))
        loop.run_until_complete(client.close())
        return result
    finally:
        loop.close()

def create_opportunity_sync(opportunity_data: Dict[str, Any]):
    """Synchronous create wrapper for Streamlit"""
    client = TaifaAPIClient()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.create_intelligence_item(opportunity_data))
        loop.run_until_complete(client.close())
        return result
    finally:
        loop.close()

def check_api_health():
    """Check API health for Streamlit"""
    client = TaifaAPIClient()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.health_check())
        loop.run_until_complete(client.close())
        return result
    finally:
        loop.close()

# Demo-specific functions
def demo_add_serper_opportunity(opportunity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Demo function to add a SERPER-discovered opportunity"""
    
    # Transform SERPER data to API format
    api_data = {
        "title": opportunity_data.get("title", ""),
        "description": opportunity_data.get("description", ""),
        "source_url": opportunity_data.get("source_url", ""),
        "status": "active",
        "geographical_scope": "Africa, Rwanda",
        "eligibility_criteria": "AI/Tech projects focusing on African development"
    }
    
    # Add optional fields if available
    if opportunity_data.get("estimated_amount"):
        # Try to parse amount (basic parsing)
        amount_str = opportunity_data["estimated_amount"]
        try:
            import re
            amount_match = re.search(r'[\d,]+', amount_str.replace('$', '').replace(',', ''))
            if amount_match:
                api_data["amount"] = float(amount_match.group())
                api_data["currency"] = "USD"
        except:
            pass
    
    return create_opportunity_sync(api_data)

# Error handling for Streamlit
def handle_api_error(func, *args, **kwargs):
    """Handle API errors gracefully in Streamlit"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        logger.error(f"Streamlit API error: {e}")
        return None

# Connection status indicator
def show_api_status():
    """Show API connection status in Streamlit"""
    with st.spinner("Checking API connection..."):
        is_healthy = check_api_health()
    
    if is_healthy:
        st.success("✅ Connected to TAIFA backend")
        return True
    else:
        st.error("❌ Cannot connect to TAIFA backend")
        st.info("Make sure the FastAPI server is running on http://localhost:8000")
        return False
