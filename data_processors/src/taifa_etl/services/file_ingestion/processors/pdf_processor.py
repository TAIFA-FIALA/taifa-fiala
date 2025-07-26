"""
PDF Processor for AI Africa Funding Tracker
==========================================

This module implements a processor for extracting funding data from PDF files.
It uses PyPDF2 for basic text extraction and a language model for structured data extraction.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

import PyPDF2
import asyncio
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Processor for extracting funding data from PDF files.
    """
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM client if available
        self.llm_client = self._initialize_llm_client()
        
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
        
    async def process(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a PDF file and extract funding data.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dict containing extracted records and metadata
        """
        self.logger.info(f"Processing PDF file: {file_path}")
        
        try:
            # Extract text from PDF
            text = self._extract_pdf_text(file_path)
            
            # Extract funding data
            if self.llm_client:
                # Use LLM for enhanced extraction
                funding_records = await self._llm_extract_funding_data(text)
            else:
                # Use regex-based extraction as fallback
                funding_records = self._extract_funding_with_regex(text)
            
            return {
                'records': funding_records,
                'source_type': 'pdf',
                'source_file': file_path.name,
                'metadata': {
                    'page_count': self._get_page_count(file_path),
                    'extraction_method': 'llm' if self.llm_client else 'regex',
                    'processed_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {file_path}: {e}")
            return {
                'records': [],
                'source_type': 'pdf',
                'source_file': file_path.name,
                'error': str(e)
            }
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
        return text
    
    def _get_page_count(self, file_path: Path) -> int:
        """
        Get the number of pages in a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Number of pages
        """
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    
    def _extract_funding_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract funding data from text using regex patterns.
        
        Args:
            text: Text to extract from
            
        Returns:
            List of extracted funding records
        """
        records = []
        
        # Regex patterns for funding amounts
        amount_patterns = [
            r'(?P<organization>[\w\s]+?)\s+(?:raised|received|secured)\s+(?P<amount>\$[\d,]+\.?\d*\s*(?:million|M|billion|B))',
            r'(?P<amount>\$[\d,]+\.?\d*\s*(?:million|M|billion|B))\s+(?:funding|investment)\s+(?:in|for)\s+(?P<organization>[\w\s]+)',
            r'(?P<organization>[\w\s]+?)\s+(?:grant|award|funding)\s+of\s+(?P<amount>\$[\d,]+\.?\d*\s*(?:million|M|billion|B)?)',
        ]
        
        for pattern in amount_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                record = {
                    'organization_name': match.group('organization').strip(),
                    'amount_text': match.group('amount'),
                    'amount_usd': self._parse_amount(match.group('amount')),
                    'context': text[max(0, match.start()-100):match.end()+100],
                    'source_type': 'pdf',
                    'extraction_method': 'regex'
                }
                records.append(record)
        
        # Extract dates
        for record in records:
            context = record['context']
            date_match = re.search(r'(?:on|dated?|as of)\s+(\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}|\w+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})', context, re.IGNORECASE)
            if date_match:
                record['date_text'] = date_match.group(1)
                record['transaction_date'] = self._parse_date(date_match.group(1))
        
        return records
    
    def _parse_amount(self, amount_text: str) -> float:
        """
        Parse amount text to a float value.
        
        Args:
            amount_text: Text containing an amount
            
        Returns:
            Parsed amount as float
        """
        amount_text = amount_text.replace('$', '').replace(',', '')
        
        multipliers = {
            'million': 1_000_000, 'M': 1_000_000, 'm': 1_000_000,
            'billion': 1_000_000_000, 'B': 1_000_000_000, 'b': 1_000_000_000
        }
        
        for key, multiplier in multipliers.items():
            if key in amount_text:
                number = float(re.search(r'[\d.]+', amount_text).group())
                return number * multiplier
        
        try:
            return float(re.search(r'[\d.]+', amount_text).group())
        except (AttributeError, ValueError):
            return 0.0
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """
        Parse date text to a standardized format.
        
        Args:
            date_text: Text containing a date
            
        Returns:
            Parsed date in ISO format or None if parsing fails
        """
        date_formats = [
            '%B %d, %Y',
            '%d %B %Y',
            '%B %d %Y',
            '%d %B, %Y',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y'
        ]
        
        # Remove ordinal suffixes
        date_text = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_text)
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_text, fmt)
                return date_obj.isoformat()[:10]  # YYYY-MM-DD
            except ValueError:
                continue
        
        return None
    
    async def _llm_extract_funding_data(self, text: str) -> List[Dict[str, Any]]:
        """
        Use a language model to extract structured funding data from text.
        
        Args:
            text: Text to extract from
            
        Returns:
            List of extracted funding records
        """
        if not self.llm_client:
            return self._extract_funding_with_regex(text)
        
        prompt = """
        Extract ALL funding transactions from this text. For each funding event, extract:
        
        1. Organization/Company name receiving funding
        2. Amount (in original currency and USD if different)
        3. Date of funding/announcement
        4. Funding stage/round (Seed, Series A, Grant, etc.)
        5. Lead investor(s)
        6. Other participating investors
        7. AI/Tech sectors or focus areas
        8. Geographic location/focus
        9. Brief description of what the funding is for
        
        Return as a JSON array of objects. Be precise with amounts and dates.
        If information is not available, use null. Extract even partial information.
        
        Text to analyze:
        {text}
        """
        
        try:
            response = await self.llm_client.messages.create(
                model="claude-3-sonnet-20240229",
                messages=[{
                    "role": "user",
                    "content": prompt.format(text=text[:15000])  # Limit text length
                }],
                max_tokens=2000,
                temperature=0.3
            )
            
            # Parse the response
            content = response.content[0].text
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                funding_data = json.loads(json_match.group())
                
                # Process each record
                processed_records = []
                for record in funding_data:
                    processed = self._process_llm_record(record)
                    if processed:
                        processed_records.append(processed)
                        
                return processed_records
            else:
                self.logger.warning("No JSON array found in LLM response")
                return self._extract_funding_with_regex(text)
                
        except Exception as e:
            self.logger.error(f"LLM extraction failed: {e}")
            return self._extract_funding_with_regex(text)
    
    def _process_llm_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process and validate LLM-extracted record.
        
        Args:
            record: Record extracted by LLM
            
        Returns:
            Processed record or None if invalid
        """
        processed = {
            'extraction_method': 'llm',
            'confidence_score': 0.7  # Default confidence for LLM extraction
        }
        
        # Map fields
        field_mapping = {
            'organization': 'organization_name',
            'company': 'organization_name',
            'amount': 'amount_original',
            'amount_usd': 'amount_usd',
            'date': 'transaction_date',
            'funding_date': 'transaction_date',
            'stage': 'funding_stage',
            'round': 'funding_stage',
            'lead_investor': 'lead_investor_name',
            'investors': 'investor_names',
            'sectors': 'ai_sectors',
            'location': 'geographic_focus',
            'description': 'project_description'
        }
        
        for llm_field, db_field in field_mapping.items():
            if llm_field in record and record[llm_field]:
                processed[db_field] = record[llm_field]
                
        # Parse amount if needed
        if 'amount_original' in processed and 'amount_usd' not in processed:
            amount_parsed = self._parse_amount(str(processed['amount_original']))
            if amount_parsed:
                processed['amount_usd'] = amount_parsed
                
        # Validate minimum fields
        if processed.get('amount_usd') or processed.get('organization_name'):
            return processed
            
        return None