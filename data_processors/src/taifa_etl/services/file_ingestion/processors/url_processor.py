"""
URL Processor for AI Africa Funding Tracker
=========================================

This module implements a processor for extracting funding data from URLs.
It uses aiohttp for asynchronous HTTP requests and BeautifulSoup for HTML parsing.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import asyncio

import aiohttp
from bs4 import BeautifulSoup
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class URLProcessor:
    """
    Processor for extracting funding data from URLs.
    """
    
    def __init__(self):
        """Initialize the URL processor."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM client if available
        self.llm_client = self._initialize_llm_client()
        
        # Initialize text processor for content processing
        from .text_processor import TextProcessor
        self.text_processor = TextProcessor()
        
    def _initialize_llm_client(self):
        """
        Initialize the language model client for enhanced extraction.
        
        Returns:
            LLM client if available, None otherwise
        """
        try:
            from anthropic import AsyncAnthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            
            if api_key:
                return AsyncAnthropic(api_key=api_key)
            else:
                self.logger.warning("ANTHROPIC_API_KEY not found, LLM extraction will be limited")
                return None
        except ImportError:
            self.logger.warning("Anthropic package not installed, LLM extraction will be limited")
            return None
        
    async def process_batch(self, urls: List[str]) -> Dict[str, Any]:
        """
        Process a batch of URLs.
        
        Args:
            urls: List of URLs to process
            
        Returns:
            Dict containing extracted records and metadata
        """
        self.logger.info(f"Processing {len(urls)} URLs")
        
        all_records = []
        failed_urls = []
        
        # Process URLs in parallel with rate limiting
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        
        async def fetch_and_process(url):
            async with semaphore:
                try:
                    content = await self._fetch_url_content(url)
                    result = await self._process_web_content(content, url)
                    return result['records']
                except Exception as e:
                    self.logger.error(f"Failed to process URL {url}: {e}")
                    failed_urls.append({'url': url, 'error': str(e)})
                    return []
                    
        tasks = [fetch_and_process(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        for records in results:
            all_records.extend(records)
            
        return {
            'records': all_records,
            'source_type': 'url',
            'metadata': {
                'total_urls': len(urls),
                'successful': len(urls) - len(failed_urls),
                'failed_urls': failed_urls,
                'processed_at': datetime.now().isoformat()
            }
        }
    
    async def process(self, url: str) -> Dict[str, Any]:
        """
        Process a single URL.
        
        Args:
            url: URL to process
            
        Returns:
            Dict containing extracted records and metadata
        """
        self.logger.info(f"Processing URL: {url}")
        
        try:
            content = await self._fetch_url_content(url)
            return await self._process_web_content(content, url)
        except Exception as e:
            self.logger.error(f"Error processing URL {url}: {e}")
            return {
                'records': [],
                'source_type': 'url',
                'source_url': url,
                'error': str(e)
            }
    
    async def _fetch_url_content(self, url: str) -> str:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; AIAfricaFundingBot/1.0)'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"HTTP {response.status}: {response.reason}")
    
    async def _process_web_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Process web page content.
        
        Args:
            html_content: HTML content to process
            url: Source URL
            
        Returns:
            Dict containing extracted records and metadata
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else "Unknown Title"
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract funding data
        if self.llm_client:
            # Use LLM for enhanced extraction
            funding_records = await self.text_processor._llm_extract_funding_data(text)
        else:
            # Use regex-based extraction as fallback
            funding_records = self.text_processor._extract_funding_with_regex(text)
        
        # Add source URL to each record
        for record in funding_records:
            record['source_url'] = url
            record['source_type'] = 'url'
        
        return {
            'records': funding_records,
            'source_type': 'url',
            'source_url': url,
            'metadata': {
                'title': title,
                'extraction_method': 'llm' if self.llm_client else 'regex',
                'processed_at': datetime.now().isoformat()
            }
        }