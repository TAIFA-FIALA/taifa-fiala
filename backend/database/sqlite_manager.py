"""
SQLite Database Manager for TAIFA-FIALA
Handles database connections and operations for n8n pipeline integration
"""

import sqlite3
import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class SQLiteManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to data directory
            project_root = Path(__file__).parent.parent.parent
            self.db_path = project_root / "data" / "taifa_fiala.db"
        else:
            self.db_path = Path(db_path)
        
        # Ensure database exists
        if not self.db_path.exists():
            logger.warning(f"Database not found at {self.db_path}. Run setup_database.py first.")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def insert_funding_opportunity(self, data: Dict[str, Any]) -> int:
        """Insert a new funding opportunity from n8n pipeline"""
        
        # Prepare data with defaults
        opportunity = {
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'organization': data.get('organization', ''),
            'amount_exact': data.get('amount_exact'),
            'amount_min': data.get('amount_min'),
            'amount_max': data.get('amount_max'),
            'currency': data.get('currency', 'USD'),
            'deadline': data.get('deadline'),
            'announcement_date': data.get('announcement_date'),
            'funding_start_date': data.get('funding_start_date'),
            'location': data.get('location', ''),
            'country': data.get('country', ''),
            'region': data.get('region', ''),
            'sector': data.get('sector', ''),
            'stage': data.get('stage', ''),
            'eligibility': data.get('eligibility', ''),
            'application_url': data.get('application_url', ''),
            'application_process': data.get('application_process', ''),
            'selection_criteria': data.get('selection_criteria', ''),
            'source_url': data.get('source_url', ''),
            'source_type': data.get('source_type', 'n8n'),
            'validation_status': data.get('validation_status', 'pending'),
            'relevance_score': data.get('relevance_score', 0.5),
            'tags': json.dumps(data.get('tags', [])) if data.get('tags') else None,
            'project_duration': data.get('project_duration', ''),
            'reporting_requirements': data.get('reporting_requirements', ''),
            'target_audience': data.get('target_audience', ''),
            'ai_subsectors': data.get('ai_subsectors', ''),
            'development_stage': data.get('development_stage', ''),
            'is_active': data.get('is_active', True),
            'is_open': data.get('is_open', True),
            'requires_registration': data.get('requires_registration', False),
            'collaboration_required': data.get('collaboration_required', False),
            'gender_focused': data.get('gender_focused', False),
            'youth_focused': data.get('youth_focused', False)
        }
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check for duplicates based on title and organization
            cursor.execute("""
                SELECT id FROM funding_opportunities 
                WHERE title = ? AND organization = ?
            """, (opportunity['title'], opportunity['organization']))
            
            existing = cursor.fetchone()
            if existing:
                logger.info(f"Duplicate opportunity found: {opportunity['title']} from {opportunity['organization']}")
                return existing['id']
            
            # Insert new opportunity
            cursor.execute("""
                INSERT INTO funding_opportunities (
                    title, description, organization, amount_exact, amount_min, amount_max,
                    currency, deadline, announcement_date, funding_start_date, location,
                    country, region, sector, stage, eligibility, application_url,
                    application_process, selection_criteria, source_url, source_type,
                    validation_status, relevance_score, tags, project_duration,
                    reporting_requirements, target_audience, ai_subsectors, development_stage,
                    is_active, is_open, requires_registration, collaboration_required,
                    gender_focused, youth_focused
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                opportunity['title'], opportunity['description'], opportunity['organization'],
                opportunity['amount_exact'], opportunity['amount_min'], opportunity['amount_max'],
                opportunity['currency'], opportunity['deadline'], opportunity['announcement_date'],
                opportunity['funding_start_date'], opportunity['location'], opportunity['country'],
                opportunity['region'], opportunity['sector'], opportunity['stage'],
                opportunity['eligibility'], opportunity['application_url'], opportunity['application_process'],
                opportunity['selection_criteria'], opportunity['source_url'], opportunity['source_type'],
                opportunity['validation_status'], opportunity['relevance_score'], opportunity['tags'],
                opportunity['project_duration'], opportunity['reporting_requirements'],
                opportunity['target_audience'], opportunity['ai_subsectors'], opportunity['development_stage'],
                opportunity['is_active'], opportunity['is_open'], opportunity['requires_registration'],
                opportunity['collaboration_required'], opportunity['gender_focused'], opportunity['youth_focused']
            ))
            
            opportunity_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Inserted funding opportunity: {opportunity['title']} (ID: {opportunity_id})")
            return opportunity_id
    
    def log_pipeline_execution(self, source_name: str, execution_id: str, status: str, 
                             records_processed: int = 0, records_inserted: int = 0, 
                             records_updated: int = 0, error_message: str = None, 
                             execution_time: float = 0.0) -> int:
        """Log n8n pipeline execution for monitoring"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get source_id
            cursor.execute("SELECT id FROM funding_sources WHERE name = ?", (source_name,))
            source = cursor.fetchone()
            source_id = source['id'] if source else None
            
            # Insert log entry
            cursor.execute("""
                INSERT INTO pipeline_logs (
                    source_id, execution_id, status, records_processed, records_inserted,
                    records_updated, error_message, execution_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source_id, execution_id, status, records_processed, records_inserted,
                records_updated, error_message, execution_time
            ))
            
            log_id = cursor.lastrowid
            conn.commit()
            
            return log_id
    
    def get_active_opportunities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get active funding opportunities for API responses"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM active_opportunities 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            opportunities = []
            for row in cursor.fetchall():
                opportunity = dict(row)
                # Parse JSON fields
                if opportunity.get('tags'):
                    opportunity['tags'] = json.loads(opportunity['tags'])
                opportunities.append(opportunity)
            
            return opportunities
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline execution statistics"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get overall stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_opportunities,
                    COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_opportunities,
                    COUNT(CASE WHEN validation_status = 'approved' THEN 1 END) as approved_opportunities,
                    COUNT(CASE WHEN DATE(deadline) >= DATE('now') THEN 1 END) as open_opportunities
                FROM funding_opportunities
            """)
            
            stats = dict(cursor.fetchone())
            
            # Get pipeline execution stats
            cursor.execute("SELECT * FROM pipeline_stats")
            pipeline_stats = [dict(row) for row in cursor.fetchall()]
            
            stats['pipeline_sources'] = pipeline_stats
            
            return stats
    
    def search_opportunities(self, query: str, sector: str = None, location: str = None, 
                           limit: int = 50) -> List[Dict[str, Any]]:
        """Search funding opportunities with filters"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            sql = """
                SELECT * FROM active_opportunities 
                WHERE (title LIKE ? OR description LIKE ? OR organization LIKE ?)
            """
            params = [f"%{query}%", f"%{query}%", f"%{query}%"]
            
            if sector:
                sql += " AND sector LIKE ?"
                params.append(f"%{sector}%")
            
            if location:
                sql += " AND (location LIKE ? OR country LIKE ? OR region LIKE ?)"
                params.extend([f"%{location}%", f"%{location}%", f"%{location}%"])
            
            sql += " ORDER BY relevance_score DESC, created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            
            opportunities = []
            for row in cursor.fetchall():
                opportunity = dict(row)
                if opportunity.get('tags'):
                    opportunity['tags'] = json.loads(opportunity['tags'])
                opportunities.append(opportunity)
            
            return opportunities

# Global instance
db_manager = SQLiteManager()