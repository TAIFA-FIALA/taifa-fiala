"""
Funding Deduplicator for AI Africa Funding Tracker
===============================================

This module implements deduplication logic for funding data to ensure
that duplicate records are not inserted into the database.
"""

import os
import logging
from typing import Dict, List, Any, Tuple, Optional
import asyncio
import hashlib
import json
from datetime import datetime, timedelta

from fuzzywuzzy import fuzz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FundingDeduplicator:
    """
    Deduplicator for funding data that uses multiple strategies to identify duplicates.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the deduplicator.
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.config = config or {
            'similarity_threshold': 85,  # Fuzzy matching threshold
            'check_window_days': 90,     # Check for duplicates within this window
            'dedup_fields': [            # Fields to use for deduplication
                'organization_name',
                'amount_usd',
                'transaction_date',
                'funding_stage'
            ]
        }
        
    async def check_duplicates(self, new_records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Check for duplicates in a list of records.
        
        Args:
            new_records: List of new records to check
            
        Returns:
            Tuple of (unique_records, duplicate_records)
        """
        self.logger.info(f"Checking {len(new_records)} records for duplicates")
        
        # Get existing records from database for comparison
        existing_records = await self._get_recent_records()
        
        unique_records = []
        duplicate_records = []
        
        # Generate deduplication hashes for new records
        for record in new_records:
            record['dedup_hash'] = self._generate_dedup_hash(record)
        
        # First pass: exact hash matching
        hash_duplicates = await self._check_hash_duplicates(new_records, existing_records)
        
        # Second pass: fuzzy matching for remaining records
        remaining_records = [r for r in new_records if r['dedup_hash'] not in hash_duplicates]
        fuzzy_unique, fuzzy_duplicates = await self._check_fuzzy_duplicates(remaining_records, existing_records)
        
        # Combine results
        unique_records = fuzzy_unique
        duplicate_records = [r for r in new_records if r['dedup_hash'] in hash_duplicates]
        duplicate_records.extend(fuzzy_duplicates)
        
        self.logger.info(f"Found {len(duplicate_records)} duplicates and {len(unique_records)} unique records")
        
        # Log duplicate information
        if duplicate_records:
            self._log_duplicates(duplicate_records)
        
        return unique_records, duplicate_records
    
    async def _get_recent_records(self) -> List[Dict[str, Any]]:
        """
        Get recent records from the database for deduplication.
        
        Returns:
            List of recent records
        """
        try:
            # Import database client
            from data_processors.db_inserter_enhanced import get_recent_transactions
            
            # Get records from the last N days
            window_days = self.config['check_window_days']
            records = await get_recent_transactions(days=window_days)
            
            self.logger.info(f"Retrieved {len(records)} recent records for deduplication")
            return records
        except Exception as e:
            self.logger.error(f"Error retrieving recent records: {e}")
            self.logger.warning("Proceeding with empty comparison set")
            return []
    
    async def _check_hash_duplicates(self, new_records: List[Dict[str, Any]], 
                                   existing_records: List[Dict[str, Any]]) -> List[str]:
        """
        Check for exact hash duplicates.
        
        Args:
            new_records: New records to check
            existing_records: Existing records to check against
            
        Returns:
            List of duplicate hashes
        """
        # Extract hashes from existing records
        existing_hashes = set()
        for record in existing_records:
            if 'dedup_hash' in record:
                existing_hashes.add(record['dedup_hash'])
            else:
                # Generate hash if not present
                record_hash = self._generate_dedup_hash(record)
                existing_hashes.add(record_hash)
        
        # Check new records against existing hashes
        duplicate_hashes = set()
        for record in new_records:
            if record['dedup_hash'] in existing_hashes:
                duplicate_hashes.add(record['dedup_hash'])
        
        return list(duplicate_hashes)
    
    async def _check_fuzzy_duplicates(self, new_records: List[Dict[str, Any]],
                                    existing_records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Check for fuzzy duplicates using multiple criteria.
        
        Args:
            new_records: New records to check
            existing_records: Existing records to check against
            
        Returns:
            Tuple of (unique_records, duplicate_records)
        """
        unique_records = []
        duplicate_records = []
        
        for new_record in new_records:
            is_duplicate, match_info = await self._is_fuzzy_duplicate(new_record, existing_records)
            
            if is_duplicate:
                new_record['duplicate_info'] = match_info
                duplicate_records.append(new_record)
            else:
                unique_records.append(new_record)
        
        return unique_records, duplicate_records
    
    async def _is_fuzzy_duplicate(self, record: Dict[str, Any], 
                                existing_records: List[Dict[str, Any]]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if a record is a fuzzy duplicate of any existing record.
        
        Args:
            record: Record to check
            existing_records: Existing records to check against
            
        Returns:
            Tuple of (is_duplicate, match_info)
        """
        best_match = {'score': 0, 'id': None, 'record': None}
        
        for existing in existing_records:
            # Calculate similarity scores
            scores = self._calculate_similarity(record, existing)
            total_score = scores['total_score']
            
            if total_score > best_match['score']:
                best_match = {
                    'score': total_score,
                    'id': existing.get('id'),
                    'record': existing,
                    'scores': scores
                }
        
        threshold = self.config['similarity_threshold']
        is_duplicate = best_match['score'] >= threshold
        
        return is_duplicate, best_match if is_duplicate else None
    
    def _calculate_similarity(self, record1: Dict[str, Any], record2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate similarity between two records.
        
        Args:
            record1: First record
            record2: Second record
            
        Returns:
            Dict with similarity scores
        """
        scores = {
            'organization': 0,
            'amount': 0,
            'date': 0,
            'stage': 0,
            'total_score': 0
        }
        
        # Organization name similarity (40% weight)
        if record1.get('organization_name') and record2.get('organization_name'):
            org_score = fuzz.token_sort_ratio(
                str(record1['organization_name']).lower(),
                str(record2['organization_name']).lower()
            )
            scores['organization'] = org_score
            scores['total_score'] += org_score * 0.4
        
        # Amount similarity (30% weight)
        amount1 = record1.get('amount_usd', 0)
        amount2 = record2.get('amount_usd', 0)
        
        if amount1 and amount2:
            # Consider amounts within 5% as matching
            ratio = min(amount1, amount2) / max(amount1, amount2) if max(amount1, amount2) > 0 else 0
            if ratio > 0.95:
                amount_score = 100
            elif ratio > 0.90:
                amount_score = 80
            elif ratio > 0.80:
                amount_score = 60
            else:
                amount_score = ratio * 60
                
            scores['amount'] = amount_score
            scores['total_score'] += amount_score * 0.3
        
        # Date proximity (20% weight)
        date1 = record1.get('transaction_date')
        date2 = record2.get('transaction_date')
        
        if date1 and date2:
            try:
                # Convert to datetime objects if they're strings
                if isinstance(date1, str):
                    date1 = datetime.fromisoformat(date1.replace('Z', '+00:00'))
                if isinstance(date2, str):
                    date2 = datetime.fromisoformat(date2.replace('Z', '+00:00'))
                
                # Calculate date difference in days
                date_diff = abs((date1 - date2).days)
                
                # Score based on proximity
                if date_diff == 0:
                    date_score = 100
                elif date_diff <= 7:
                    date_score = 90
                elif date_diff <= 30:
                    date_score = 70
                elif date_diff <= 90:
                    date_score = 50
                else:
                    date_score = 30
                    
                scores['date'] = date_score
                scores['total_score'] += date_score * 0.2
            except (ValueError, TypeError):
                # Handle date parsing errors
                pass
        
        # Funding stage (10% weight)
        stage1 = record1.get('funding_stage', '').lower()
        stage2 = record2.get('funding_stage', '').lower()
        
        if stage1 and stage2:
            stage_score = fuzz.ratio(stage1, stage2)
            scores['stage'] = stage_score
            scores['total_score'] += stage_score * 0.1
        
        return scores
    
    def _generate_dedup_hash(self, record: Dict[str, Any]) -> str:
        """
        Generate a deduplication hash for a record.
        
        Args:
            record: Record to generate hash for
            
        Returns:
            Deduplication hash
        """
        # Create a canonical representation
        canonical = {}
        
        # Organization name (normalized)
        if 'organization_name' in record and record['organization_name']:
            canonical['org'] = record['organization_name'].lower().strip()
        
        # Amount (rounded to nearest 1000)
        if 'amount_usd' in record and record['amount_usd']:
            try:
                amount = float(record['amount_usd'])
                canonical['amount'] = round(amount, -3)  # Round to nearest 1000
            except (ValueError, TypeError):
                pass
        
        # Date (just date part)
        if 'transaction_date' in record and record['transaction_date']:
            try:
                if isinstance(record['transaction_date'], str):
                    canonical['date'] = record['transaction_date'][:10]  # YYYY-MM-DD
                else:
                    canonical['date'] = record['transaction_date'].isoformat()[:10]
            except (ValueError, TypeError, AttributeError):
                pass
        
        # Funding stage
        if 'funding_stage' in record and record['funding_stage']:
            canonical['stage'] = record['funding_stage'].lower().strip()
        
        # Create hash
        hash_string = json.dumps(canonical, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def _log_duplicates(self, duplicate_records: List[Dict[str, Any]]):
        """
        Log information about duplicate records.
        
        Args:
            duplicate_records: List of duplicate records
        """
        log_path = os.path.join('data_ingestion', 'logs', 'duplicates.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, 'a') as f:
            for record in duplicate_records:
                timestamp = datetime.now().isoformat()
                match_info = record.get('duplicate_info', {})
                
                log_entry = {
                    'timestamp': timestamp,
                    'new_record': {
                        'organization': record.get('organization_name'),
                        'amount': record.get('amount_usd'),
                        'date': record.get('transaction_date'),
                        'source': record.get('source_type')
                    },
                    'matched_record': {
                        'id': match_info.get('id'),
                        'organization': match_info.get('record', {}).get('organization_name'),
                        'amount': match_info.get('record', {}).get('amount_usd'),
                        'date': match_info.get('record', {}).get('transaction_date')
                    },
                    'similarity_scores': match_info.get('scores', {})
                }
                
                f.write(json.dumps(log_entry) + '\n')