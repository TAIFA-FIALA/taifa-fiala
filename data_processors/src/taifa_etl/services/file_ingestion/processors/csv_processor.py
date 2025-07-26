"""
CSV Processor for AI Africa Funding Tracker
=========================================

This module implements a processor for extracting funding data from CSV files.
It uses pandas for data processing and includes intelligent column detection.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

import pandas as pd
import chardet
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVProcessor:
    """
    Processor for extracting funding data from CSV files.
    """
    
    def __init__(self):
        """Initialize the CSV processor."""
        self.logger = logging.getLogger(__name__)
        
    async def process(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a CSV file and extract funding data.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dict containing extracted records and metadata
        """
        self.logger.info(f"Processing CSV file: {file_path}")
        
        try:
            # Detect encoding
            encoding = self._detect_encoding(file_path)
            
            # Read CSV with detected encoding
            df = pd.read_csv(file_path, encoding=encoding)
            
            # Clean column names
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            # Detect funding-related columns
            column_mapping = self._detect_funding_columns(df)
            
            self.logger.info(f"Detected columns: {column_mapping}")
            
            # Extract records
            funding_records = []
            
            for _, row in df.iterrows():
                record = await self._extract_funding_record_from_row(row, column_mapping)
                if record:
                    funding_records.append(record)
            
            return {
                'records': funding_records,
                'source_type': 'csv',
                'source_file': file_path.name,
                'metadata': {
                    'row_count': len(df),
                    'extracted_count': len(funding_records),
                    'columns_mapped': column_mapping,
                    'processed_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error processing CSV {file_path}: {e}")
            return {
                'records': [],
                'source_type': 'csv',
                'source_file': file_path.name,
                'error': str(e)
            }
    
    def _detect_encoding(self, file_path: Path) -> str:
        """
        Detect the encoding of a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Detected encoding
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            
        return encoding or 'utf-8'
    
    def _detect_funding_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Intelligently detect which columns contain funding data.
        
        Args:
            df: DataFrame containing the CSV data
            
        Returns:
            Dict mapping field types to column names
        """
        column_mapping = {}
        
        # Patterns for different field types
        patterns = {
            'organization': {
                'keywords': ['company', 'startup', 'organization', 'org', 'recipient', 
                            'portfolio', 'name', 'beneficiary'],
                'priority': ['company_name', 'organization_name', 'startup_name', 'company']
            },
            'amount': {
                'keywords': ['amount', 'funding', 'investment', 'raised', 'size', 
                            'value', 'capital', 'money'],
                'priority': ['funding_amount', 'amount_raised', 'investment_amount', 'amount']
            },
            'date': {
                'keywords': ['date', 'announced', 'closed', 'when', 'year', 'month'],
                'priority': ['funding_date', 'announcement_date', 'date_announced', 'date']
            },
            'stage': {
                'keywords': ['round', 'series', 'stage', 'type', 'phase'],
                'priority': ['funding_round', 'investment_stage', 'series', 'round']
            },
            'investor': {
                'keywords': ['investor', 'funder', 'lead', 'participants', 'vc', 'fund'],
                'priority': ['lead_investor', 'investors', 'investor_name', 'funder']
            },
            'sector': {
                'keywords': ['sector', 'industry', 'category', 'vertical', 'domain', 'field'],
                'priority': ['sector', 'industry', 'ai_domain', 'category']
            },
            'country': {
                'keywords': ['country', 'location', 'geography', 'nation', 'hq'],
                'priority': ['country', 'headquarters_country', 'location', 'geography']
            }
        }
        
        # Check each column against patterns
        for col in df.columns:
            col_lower = col.lower()
            
            for field_type, pattern_info in patterns.items():
                # First check priority matches
                if col_lower in pattern_info['priority']:
                    column_mapping[field_type] = col
                    break
                    
                # Then check keyword matches
                elif any(keyword in col_lower for keyword in pattern_info['keywords']):
                    if field_type not in column_mapping:  # Don't override priority matches
                        column_mapping[field_type] = col
                        
        # Validate we have minimum required fields
        if 'amount' not in column_mapping:
            # Try to find any column with numeric data that might be amounts
            for col in df.columns:
                if df[col].dtype in ['float64', 'int64'] and df[col].max() > 1000:
                    column_mapping['amount'] = col
                    break
                    
        return column_mapping
    
    async def _extract_funding_record_from_row(self, row: pd.Series, 
                                            column_mapping: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Extract a funding record from a CSV row.
        
        Args:
            row: Row from the CSV
            column_mapping: Mapping of field types to column names
            
        Returns:
            Extracted record or None if invalid
        """
        record = {}
        
        # Extract mapped fields
        if 'organization' in column_mapping:
            record['organization_name'] = str(row[column_mapping['organization']]).strip()
            
        if 'amount' in column_mapping:
            amount_val = row[column_mapping['amount']]
            amount_parsed = self._parse_amount(str(amount_val))
            if amount_parsed:
                record['amount_usd'] = amount_parsed
                record['amount_original'] = amount_val
                
        if 'date' in column_mapping:
            date_parsed = self._parse_date(str(row[column_mapping['date']]))
            if date_parsed:
                record['transaction_date'] = date_parsed
                record['announcement_date'] = date_parsed
                
        if 'stage' in column_mapping:
            record['funding_stage'] = str(row[column_mapping['stage']]).strip()
            
        if 'investor' in column_mapping:
            investor_val = str(row[column_mapping['investor']])
            record['lead_investor_name'] = investor_val
            
        if 'sector' in column_mapping:
            sectors = str(row[column_mapping['sector']]).split(',')
            record['ai_sectors'] = [s.strip() for s in sectors if s.strip()]
            
        if 'country' in column_mapping:
            record['geographic_focus'] = [str(row[column_mapping['country']]).strip()]
            
        # Add metadata
        record['extraction_method'] = 'csv_import'
        record['confidence_score'] = 0.9  # High confidence for structured data
        record['source_type'] = 'csv'
        
        # Only return if we have essential fields
        if record.get('amount_usd') or record.get('organization_name'):
            return record
            
        return None
    
    def _parse_amount(self, amount_text: str) -> Optional[float]:
        """
        Parse amount strings into USD float.
        
        Args:
            amount_text: Text containing an amount
            
        Returns:
            Parsed amount as float or None if parsing fails
        """
        if not amount_text or amount_text.lower() in ['nan', 'none', 'n/a', '-']:
            return None
            
        # Remove currency symbols and spaces
        cleaned = amount_text.replace('$', '').replace('€', '').replace('£', '')
        cleaned = cleaned.replace(',', '').replace(' ', '').strip()
        
        # Handle different formats
        multipliers = {
            'k': 1_000,
            'm': 1_000_000,
            'mil': 1_000_000,
            'million': 1_000_000,
            'mn': 1_000_000,
            'b': 1_000_000_000,
            'billion': 1_000_000_000,
            'bn': 1_000_000_000
        }
        
        # Check for multiplier
        for suffix, multiplier in multipliers.items():
            if cleaned.lower().endswith(suffix):
                try:
                    number_part = cleaned[:-len(suffix)].strip()
                    return float(number_part) * multiplier
                except ValueError:
                    continue
                    
        # Try direct conversion
        try:
            return float(cleaned)
        except ValueError:
            # Try extracting first number
            match = re.search(r'[\d,]+\.?\d*', amount_text)
            if match:
                try:
                    return float(match.group().replace(',', ''))
                except ValueError:
                    pass
                    
        return None
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """
        Parse date strings into ISO format.
        
        Args:
            date_text: Text containing a date
            
        Returns:
            Parsed date in ISO format or None if parsing fails
        """
        if not date_text or date_text.lower() in ['nan', 'none', 'n/a', '-']:
            return None
            
        # Common date formats to try
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%m-%d-%Y',
            '%Y/%m/%d',
            '%d %B %Y',
            '%B %d, %Y',
            '%d %b %Y',
            '%b %d, %Y',
            '%Y'  # Just year
        ]
        
        date_text = date_text.strip()
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_text, fmt)
                return date_obj.isoformat()[:10]  # YYYY-MM-DD
            except ValueError:
                continue
                
        # Try pandas parser as fallback
        try:
            date_obj = pd.to_datetime(date_text)
            return date_obj.isoformat()[:10]  # YYYY-MM-DD
        except:
            pass
            
        return None