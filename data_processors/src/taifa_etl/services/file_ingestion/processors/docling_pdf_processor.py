"""
Enhanced PDF Processor using Docling for AI Africa Funding Tracker
================================================================

This module implements a more sophisticated processor for extracting funding data from PDF files
using Docling, which provides better text extraction, table handling, and document structure understanding.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import re
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DoclingPDFProcessor:
    """
    Enhanced processor for extracting funding data from PDF files using Docling.
    """
    
    def __init__(self):
        """Initialize the Docling PDF processor."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize Docling
        try:
            from docling.document_converter import DocumentConverter
            
            # Use basic configuration to avoid dependency issues
            self.converter = DocumentConverter()
            
            self.logger.info("Docling PDF processor initialized successfully")
            
        except ImportError as e:
            self.logger.error(f"Failed to import Docling: {e}")
            raise ImportError("Docling package not installed. Please install with: pip install docling")
        except Exception as e:
            self.logger.error(f"Failed to initialize Docling: {e}")
            # Fall back to simpler initialization
            try:
                from docling.document_converter import DocumentConverter
                self.converter = DocumentConverter()
                self.logger.warning("Docling initialized with basic configuration")
            except:
                raise ImportError("Docling initialization failed")
        
        # Initialize LLM client if available
        self.llm_client = self._initialize_llm_client()
        
    def _initialize_llm_client(self):
        """
        Initialize the language model client for enhanced extraction.
        Supports multiple LLM providers.
        
        Returns:
            LLM client if available, None otherwise
        """
        # Try multiple LLM providers in order of preference
        llm_providers = [
            ("ANTHROPIC_API_KEY", self._init_anthropic),
            ("OPENAI_API_KEY", self._init_openai),
            ("GEMINI_API_KEY", self._init_gemini),
            ("DEEPSEEK_API_KEY", self._init_deepseek),
        ]
        
        for api_key_name, init_func in llm_providers:
            api_key = os.environ.get(api_key_name)
            if api_key:
                try:
                    client = init_func(api_key)
                    self.logger.info(f"Initialized LLM client: {api_key_name}")
                    return client
                except Exception as e:
                    self.logger.warning(f"Failed to initialize {api_key_name}: {e}")
                    continue
        
        self.logger.warning("No LLM client available, using rule-based extraction only")
        return None
    
    def _init_anthropic(self, api_key: str):
        """Initialize Anthropic client."""
        from anthropic import AsyncAnthropic
        return AsyncAnthropic(api_key=api_key)
    
    def _init_openai(self, api_key: str):
        """Initialize OpenAI client."""
        from openai import AsyncOpenAI
        return AsyncOpenAI(api_key=api_key)
    
    def _init_gemini(self, api_key: str):
        """Initialize Gemini client."""
        # Note: This would require google-generativeai package
        self.logger.warning("Gemini client not implemented yet")
        return None
    
    def _init_deepseek(self, api_key: str):
        """Initialize DeepSeek client."""
        # Note: This would require the appropriate DeepSeek client
        self.logger.warning("DeepSeek client not implemented yet")
        return None
        
    async def process(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a PDF file and extract funding data using Docling.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dict containing extracted records and metadata
        """
        self.logger.info(f"Processing PDF file with Docling: {file_path}")
        
        try:
            # Convert PDF using Docling
            conversion_result = self.converter.convert(file_path)
            
            # Extract structured content
            doc = conversion_result.document
            
            # Get text content
            text_content = doc.export_to_markdown()
            
            # Extract tables if any
            tables = self._extract_tables(doc)
            
            # Extract funding data using multiple approaches
            funding_records = []
            
            # 1. Extract from text using improved regex patterns
            text_records = self._extract_funding_with_enhanced_regex(text_content)
            funding_records.extend(text_records)
            
            # 2. Extract from tables
            table_records = self._extract_funding_from_tables(tables)
            funding_records.extend(table_records)
            
            # 3. Use LLM for enhanced extraction if available
            if self.llm_client and funding_records:
                # Use LLM to enhance and validate extracted records
                enhanced_records = await self._enhance_with_llm(text_content, funding_records)
                funding_records = enhanced_records
            elif self.llm_client:
                # Use LLM for primary extraction
                llm_records = await self._llm_extract_funding_data(text_content)
                funding_records.extend(llm_records)
            
            # Deduplicate and clean records
            funding_records = self._deduplicate_records(funding_records)
            
            return {
                'records': funding_records,
                'source_type': 'pdf',
                'source_file': file_path.name,
                'metadata': {
                    'page_count': len(doc.pages) if hasattr(doc, 'pages') else 0,
                    'extraction_method': 'docling_enhanced',
                    'tables_found': len(tables),
                    'text_length': len(text_content),
                    'llm_used': self.llm_client is not None,
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
    
    def _extract_tables(self, doc) -> List[Dict]:
        """
        Extract tables from the document.
        
        Args:
            doc: Docling document object
            
        Returns:
            List of table data
        """
        tables = []
        
        try:
            # Extract tables from Docling document
            for element in doc.body.elements:
                if hasattr(element, 'label') and 'table' in element.label.lower():
                    table_data = self._parse_table_element(element)
                    if table_data:
                        tables.append(table_data)
        except Exception as e:
            self.logger.warning(f"Error extracting tables: {e}")
        
        return tables
    
    def _parse_table_element(self, element) -> Optional[Dict]:
        """
        Parse a table element into structured data.
        
        Args:
            element: Table element from Docling
            
        Returns:
            Parsed table data or None
        """
        try:
            # This is a simplified implementation
            # Real implementation would depend on Docling's table structure
            return {
                'type': 'table',
                'content': str(element),
                'rows': []  # Would extract actual rows/columns
            }
        except Exception as e:
            self.logger.warning(f"Error parsing table element: {e}")
            return None
    
    def _extract_funding_with_enhanced_regex(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract funding data from text using enhanced regex patterns optimized for funding reports.
        
        Args:
            text: Text to extract from
            
        Returns:
            List of extracted funding records
        """
        records = []
        
        # Enhanced regex patterns for various funding formats
        funding_patterns = [
            # Aggregate funding patterns (like "X startups raised $Y")
            r'(?P<count>\d+)\s+(?P<org_type>African tech startups?|startups?|companies?)\s+raised\s+.*?(?P<amount>US\$[\d,]+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:million|billion|M|B))?)',
            
            # Individual funding patterns
            r'(?P<organization>[\w\s&\.\-]+?)\s+(?:raised|received|secured|closed)\s+(?P<amount>(?:US\$|USD\s*)?[\d,]+(?:\.\d+)?\s*(?:million|billion|M|B|k))',
            r'(?P<amount>(?:US\$|USD\s*)?[\d,]+(?:\.\d+)?\s*(?:million|billion|M|B|k))\s+(?:funding|investment|round)\s+(?:in|for|by)\s+(?P<organization>[\w\s&\.\-]+)',
            
            # Series/round specific patterns
            r'(?P<organization>[\w\s&\.\-]+?)\s+(?:completed|closed|announced)\s+(?:its\s+)?(?P<round_type>Series\s+[A-Z]|seed|pre-seed|bridge)\s+(?:round\s+)?(?:of\s+)?(?P<amount>(?:US\$|USD\s*)?[\d,]+(?:\.\d+)?\s*(?:million|billion|M|B|k))',
            
            # Investment/acquisition patterns
            r'(?P<investor>[\w\s&\.\-]+?)\s+(?:invested|acquired|led)\s+(?P<amount>(?:US\$|USD\s*)?[\d,]+(?:\.\d+)?\s*(?:million|billion|M|B|k))\s+(?:in|into)\s+(?P<organization>[\w\s&\.\-]+)',
            
            # Grant and award patterns
            r'(?P<organization>[\w\s&\.\-]+?)\s+(?:received|awarded|granted)\s+(?:a\s+)?(?P<amount>(?:US\$|USD\s*)?[\d,]+(?:\.\d+)?\s*(?:million|billion|M|B|k))\s+(?:grant|award|funding)',
            
            # Large number formats (like US$3,333,071,000)
            r'(?P<amount>US\$[\d,]+(?:,\d{3})*(?:\.\d+)?)',
            
            # Revenue and valuation mentions
            r'(?P<organization>[\w\s&\.\-]+?)\s+(?:valued|worth)\s+(?:at\s+)?(?P<amount>(?:US\$|USD\s*)?[\d,]+(?:\.\d+)?\s*(?:million|billion|M|B))',
        ]
        
        for pattern in funding_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                groups = match.groupdict()
                
                # Extract organization name
                org_name = groups.get('organization', '').strip()
                if not org_name:
                    org_name = groups.get('org_type', 'African tech startups').strip()
                
                # Parse amount
                amount_text = groups.get('amount', '')
                amount_usd = self._parse_amount(amount_text)
                
                # Skip if amount is too small or too large (likely parsing errors)
                if amount_usd < 1000 or amount_usd > 100_000_000_000:
                    continue
                
                record = {
                    'organization_name': org_name,
                    'amount_text': amount_text,
                    'amount_usd': amount_usd,
                    'round_type': groups.get('round_type', ''),
                    'investor': groups.get('investor', ''),
                    'count': groups.get('count', ''),
                    'context': text[max(0, match.start()-150):match.end()+150],
                    'source_type': 'pdf',
                    'extraction_method': 'docling_regex'
                }
                
                # Extract date from context
                self._extract_date_from_context(record)
                
                records.append(record)
        
        return records
    
    def _extract_funding_from_tables(self, tables: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract funding data from tables.
        
        Args:
            tables: List of table data
            
        Returns:
            List of extracted funding records
        """
        records = []
        
        # This is a placeholder - real implementation would parse table structures
        # looking for columns like "Company", "Amount", "Round", "Date", etc.
        
        for table in tables:
            # Simple extraction from table content
            table_text = str(table.get('content', ''))
            if any(keyword in table_text.lower() for keyword in ['funding', 'raised', 'investment', 'million', 'startup']):
                # Extract using regex patterns on table content
                table_records = self._extract_funding_with_enhanced_regex(table_text)
                for record in table_records:
                    record['extraction_method'] = 'docling_table'
                records.extend(table_records)
        
        return records
    
    def _parse_amount(self, amount_text: str) -> float:
        """
        Parse amount text to a float value, handling multiple formats.
        
        Args:
            amount_text: Text containing an amount
            
        Returns:
            Parsed amount as float in USD
        """
        if not amount_text:
            return 0.0
        
        # Clean the text
        clean_text = amount_text.replace('US$', '').replace('USD', '').replace('$', '').replace(',', '').strip()
        
        # Handle multipliers
        multipliers = {
            'billion': 1_000_000_000, 'B': 1_000_000_000, 'b': 1_000_000_000,
            'million': 1_000_000, 'M': 1_000_000, 'm': 1_000_000,
            'thousand': 1_000, 'K': 1_000, 'k': 1_000,
        }
        
        multiplier = 1
        for key, mult in multipliers.items():
            if key in clean_text:
                multiplier = mult
                clean_text = clean_text.replace(key, '').strip()
                break
        
        # Extract the numeric value
        try:
            # Find the main number
            number_match = re.search(r'[\d,]+\.?\d*', clean_text)
            if number_match:
                number_str = number_match.group().replace(',', '')
                number = float(number_str)
                return number * multiplier
        except (ValueError, AttributeError):
            pass
        
        return 0.0
    
    def _extract_date_from_context(self, record: Dict[str, Any]):
        """
        Extract date information from the record's context.
        
        Args:
            record: Record to update with date information
        """
        context = record.get('context', '')
        
        # Date patterns
        date_patterns = [
            r'(?:in|during|for)\s+(\d{4})',  # Year only
            r'(\w+\s+\d{1,2},?\s+\d{4})',   # Month Day, Year
            r'(\d{1,2}/\d{1,2}/\d{4})',     # MM/DD/YYYY
            r'(\d{4}-\d{2}-\d{2})',         # YYYY-MM-DD
            r'(Q[1-4]\s+\d{4})',            # Quarter Year
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                record['date_text'] = match.group(1)
                record['transaction_date'] = self._parse_date(match.group(1))
                break
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """
        Parse date text to a standardized format.
        
        Args:
            date_text: Text containing a date
            
        Returns:
            Parsed date in ISO format or None if parsing fails
        """
        if not date_text:
            return None
        
        # Handle year-only format
        if re.match(r'^\d{4}$', date_text.strip()):
            return f"{date_text.strip()}-01-01"
        
        # Handle quarter format (Q1 2022 -> 2022-01-01)
        quarter_match = re.match(r'Q([1-4])\s+(\d{4})', date_text, re.IGNORECASE)
        if quarter_match:
            quarter, year = quarter_match.groups()
            quarter_months = {'1': '01', '2': '04', '3': '07', '4': '10'}
            return f"{year}-{quarter_months[quarter]}-01"
        
        # Standard date parsing
        date_formats = [
            '%B %d, %Y', '%d %B %Y', '%B %d %Y', '%d %B, %Y',
            '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'
        ]
        
        # Remove ordinal suffixes
        clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_text)
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(clean_date.strip(), fmt)
                return date_obj.isoformat()[:10]  # YYYY-MM-DD
            except ValueError:
                continue
        
        return None
    
    def _deduplicate_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate records based on organization name and amount.
        
        Args:
            records: List of funding records
            
        Returns:
            Deduplicated list of records
        """
        seen = set()
        unique_records = []
        
        for record in records:
            # Create a key based on organization and amount
            key = (
                record.get('organization_name', '').lower().strip(),
                record.get('amount_usd', 0)
            )
            
            if key not in seen and key[0] and key[1] > 0:
                seen.add(key)
                unique_records.append(record)
        
        return unique_records
    
    async def _enhance_with_llm(self, text: str, existing_records: List[Dict]) -> List[Dict[str, Any]]:
        """
        Use LLM to enhance and validate existing records.
        
        Args:
            text: Full document text
            existing_records: Records found by regex
            
        Returns:
            Enhanced list of records
        """
        # This would implement LLM-based enhancement
        # For now, return existing records
        return existing_records
    
    async def _llm_extract_funding_data(self, text: str) -> List[Dict[str, Any]]:
        """
        Use LLM for primary funding data extraction.
        
        Args:
            text: Text to extract from
            
        Returns:
            List of extracted funding records
        """
        # This would implement LLM-based extraction
        # For now, return empty list
        return []
