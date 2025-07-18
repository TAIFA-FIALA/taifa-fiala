"""
Database Optimization Layer for High-Throughput Operations
=========================================================

Optimized database operations for rapid scaling with:
- Connection pooling and management
- Batch operations for bulk inserts/updates
- Optimized queries with proper indexing
- Read replicas and caching strategies
- Transaction management for data consistency
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from dataclasses import dataclass
import asyncpg
import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from sqlalchemy import Index, func, and_, or_
import redis.asyncio as redis

from app.models.funding import AfricaIntelligenceItem, FundingType
from app.models.organization import Organization
from app.models.validation import ValidationResult as ValidationResultModel
from app.core.data_validation import ValidationResult, ValidationStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

@dataclass
class DatabaseConfig:
    """Configuration for database optimization"""
    
    # Connection Pool Settings
    pool_size: int = 50
    max_overflow: int = 100
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    
    # Batch Processing Settings
    batch_size: int = 1000
    max_parallel_operations: int = 20
    bulk_insert_batch_size: int = 500
    
    # Query Optimization
    query_timeout: int = 30
    enable_query_cache: bool = True
    cache_ttl: int = 300  # 5 minutes
    
    # Read Replica Settings
    read_replica_url: Optional[str] = None
    read_write_split: bool = True
    
    # Performance Monitoring
    log_slow_queries: bool = True
    slow_query_threshold: float = 1.0  # seconds

# =============================================================================
# CONNECTION POOL MANAGER
# =============================================================================

class DatabaseManager:
    """Optimized database connection manager"""
    
    def __init__(self, config: DatabaseConfig, database_url: str):
        self.config = config
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self.read_engine = None
        self.read_session_factory = None
        self.redis_client = None
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize database connections and pools"""
        try:
            # Primary database engine (read/write)
            self.engine = create_async_engine(
                self.database_url,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=self.config.pool_pre_ping,
                echo=False,  # Set to True for SQL debugging
                future=True
            )
            
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Read replica engine (if configured)
            if self.config.read_replica_url:
                self.read_engine = create_async_engine(
                    self.config.read_replica_url,
                    pool_size=self.config.pool_size // 2,
                    max_overflow=self.config.max_overflow // 2,
                    pool_timeout=self.config.pool_timeout,
                    pool_recycle=self.config.pool_recycle,
                    pool_pre_ping=self.config.pool_pre_ping,
                    echo=False,
                    future=True
                )
                
                self.read_session_factory = async_sessionmaker(
                    self.read_engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
            
            # Redis for caching
            if self.config.enable_query_cache:
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    decode_responses=True
                )
                await self.redis_client.ping()
            
            # Test connections
            await self._test_connections()
            
            self.logger.info("Database manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _test_connections(self):
        """Test database connections"""
        async with self.get_session() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        
        if self.read_session_factory:
            async with self.get_read_session() as session:
                result = await session.execute(text("SELECT 1"))
                assert result.scalar() == 1
    
    @asynccontextmanager
    async def get_session(self, read_only: bool = False):
        """Get database session with proper cleanup"""
        if read_only and self.read_session_factory:
            session_factory = self.read_session_factory
        else:
            session_factory = self.session_factory
            
        async with session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_read_session(self):
        """Get read-only session for queries"""
        async with self.get_session(read_only=True) as session:
            yield session
    
    async def close(self):
        """Close all database connections"""
        if self.engine:
            await self.engine.dispose()
        if self.read_engine:
            await self.read_engine.dispose()
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("Database connections closed")

# =============================================================================
# OPTIMIZED CRUD OPERATIONS
# =============================================================================

class OptimizedCRUD:
    """Optimized CRUD operations for high-throughput scenarios"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.config = db_manager.config
        self.logger = logging.getLogger(__name__)
    
    async def bulk_insert_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[int]:
        """Bulk insert intelligence feed with optimization"""
        try:
            inserted_ids = []
            
            # Process in batches
            for i in range(0, len(opportunities), self.config.bulk_insert_batch_size):
                batch = opportunities[i:i + self.config.bulk_insert_batch_size]
                
                async with self.db_manager.get_session() as session:
                    # Prepare batch data
                    batch_data = []
                    for opp in batch:
                        # Add timestamps
                        opp['created_at'] = datetime.utcnow()
                        opp['updated_at'] = datetime.utcnow()
                        batch_data.append(opp)
                    
                    # Use PostgreSQL's INSERT ... ON CONFLICT for upsert
                    stmt = insert(AfricaIntelligenceItem).values(batch_data)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['title', 'organization_id'],
                        set_=dict(
                            description=stmt.excluded.description,
                            amount_usd=stmt.excluded.amount_usd,
                            deadline=stmt.excluded.deadline,
                            updated_at=stmt.excluded.updated_at
                        )
                    ).returning(AfricaIntelligenceItem.id)
                    
                    result = await session.execute(stmt)
                    batch_ids = [row[0] for row in result.fetchall()]
                    inserted_ids.extend(batch_ids)
                    
                    await session.commit()
                    
                    self.logger.info(f"Bulk inserted batch of {len(batch)} opportunities")
            
            return inserted_ids
            
        except Exception as e:
            self.logger.error(f"Bulk insert failed: {e}")
            raise
    
    async def bulk_update_validation_results(self, validation_results: List[ValidationResult]) -> int:
        """Bulk update validation results"""
        try:
            updated_count = 0
            
            for i in range(0, len(validation_results), self.config.bulk_insert_batch_size):
                batch = validation_results[i:i + self.config.bulk_insert_batch_size]
                
                async with self.db_manager.get_session() as session:
                    # Prepare batch data
                    batch_data = []
                    for result in batch:
                        validation_data = {
                            'id': result.id,
                            'status': result.status.value,
                            'confidence_score': result.confidence_score,
                            'validation_notes': result.validation_notes,
                            'requires_human_review': result.requires_human_review,
                            'validated_data': result.validated_data,
                            'created_at': datetime.utcnow()
                        }
                        batch_data.append(validation_data)
                    
                    # Bulk upsert
                    stmt = insert(ValidationResultModel).values(batch_data)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['id'],
                        set_=dict(
                            status=stmt.excluded.status,
                            confidence_score=stmt.excluded.confidence_score,
                            validation_notes=stmt.excluded.validation_notes,
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    await session.execute(stmt)
                    await session.commit()
                    
                    updated_count += len(batch)
                    
                    self.logger.info(f"Bulk updated batch of {len(batch)} validation results")
            
            return updated_count
            
        except Exception as e:
            self.logger.error(f"Bulk update validation results failed: {e}")
            raise
    
    async def get_opportunities_for_review(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get opportunities pending review with optimized query"""
        try:
            cache_key = f"opportunities_review:{limit}"
            
            # Check cache first
            if self.db_manager.redis_client:
                cached_result = await self.db_manager.redis_client.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
            
            async with self.db_manager.get_read_session() as session:
                # Optimized query with proper joins
                query = text("""
                    SELECT 
                        fo.id,
                        fo.title,
                        fo.description,
                        fo.amount_usd,
                        fo.deadline,
                        fo.created_at,
                        o.name as organization_name,
                        vr.status as validation_status,
                        vr.confidence_score,
                        vr.validation_notes
                    FROM africa_intelligence_feed fo
                    LEFT JOIN organizations o ON fo.organization_id = o.id
                    LEFT JOIN validation_results vr ON vr.opportunity_id = fo.id
                    WHERE vr.status = 'needs_review'
                    ORDER BY fo.created_at DESC
                    LIMIT :limit
                """)
                
                result = await session.execute(query, {'limit': limit})
                opportunities = [dict(row) for row in result.fetchall()]
                
                # Cache result
                if self.db_manager.redis_client:
                    await self.db_manager.redis_client.setex(
                        cache_key, 
                        self.config.cache_ttl, 
                        json.dumps(opportunities, default=str)
                    )
                
                return opportunities
                
        except Exception as e:
            self.logger.error(f"Get opportunities for review failed: {e}")
            raise
    
    async def search_opportunities_optimized(self, 
                                           search_params: Dict[str, Any], 
                                           limit: int = 50, 
                                           offset: int = 0) -> Dict[str, Any]:
        """Optimized search with full-text search and filtering"""
        try:
            # Create cache key from search params
            cache_key = f"search:{hash(str(sorted(search_params.items())))}:{limit}:{offset}"
            
            # Check cache
            if self.db_manager.redis_client:
                cached_result = await self.db_manager.redis_client.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
            
            async with self.db_manager.get_read_session() as session:
                # Build dynamic query
                base_query = """
                    SELECT 
                        fo.id,
                        fo.title,
                        fo.description,
                        fo.amount_usd,
                        fo.currency,
                        fo.deadline,
                        fo.status,
                        fo.created_at,
                        o.name as organization_name,
                        o.country,
                        ft.name as funding_type,
                        ts_rank(search_vector, plainto_tsquery(:search_text)) as relevance
                    FROM africa_intelligence_feed fo
                    LEFT JOIN organizations o ON fo.organization_id = o.id
                    LEFT JOIN funding_types ft ON fo.funding_type_id = ft.id
                    WHERE 1=1
                """
                
                conditions = []
                params = {}
                
                # Full-text search
                if search_params.get('keyword'):
                    conditions.append("search_vector @@ plainto_tsquery(:search_text)")
                    params['search_text'] = search_params['keyword']
                
                # Amount range
                if search_params.get('min_amount'):
                    conditions.append("fo.amount_usd >= :min_amount")
                    params['min_amount'] = search_params['min_amount']
                
                if search_params.get('max_amount'):
                    conditions.append("fo.amount_usd <= :max_amount")
                    params['max_amount'] = search_params['max_amount']
                
                # Deadline range
                if search_params.get('deadline_after'):
                    conditions.append("fo.deadline >= :deadline_after")
                    params['deadline_after'] = search_params['deadline_after']
                
                # Status filter
                if search_params.get('status'):
                    conditions.append("fo.status = :status")
                    params['status'] = search_params['status']
                
                # Country filter
                if search_params.get('country'):
                    conditions.append("o.country = :country")
                    params['country'] = search_params['country']
                
                # Funding type filter
                if search_params.get('funding_type'):
                    conditions.append("ft.category = :funding_type")
                    params['funding_type'] = search_params['funding_type']
                
                # Add conditions to query
                if conditions:
                    base_query += " AND " + " AND ".join(conditions)
                
                # Add ordering and pagination
                if search_params.get('keyword'):
                    base_query += " ORDER BY relevance DESC, fo.created_at DESC"
                else:
                    base_query += " ORDER BY fo.created_at DESC"
                
                base_query += " LIMIT :limit OFFSET :offset"
                params['limit'] = limit
                params['offset'] = offset
                
                # Execute query
                result = await session.execute(text(base_query), params)
                opportunities = [dict(row) for row in result.fetchall()]
                
                # Get total count
                count_query = base_query.replace(
                    "SELECT fo.id, fo.title, fo.description, fo.amount_usd, fo.currency, fo.deadline, fo.status, fo.created_at, o.name as organization_name, o.country, ft.name as funding_type, ts_rank(search_vector, plainto_tsquery(:search_text)) as relevance",
                    "SELECT COUNT(*)"
                ).split("ORDER BY")[0].split("LIMIT")[0]
                
                count_result = await session.execute(text(count_query), {k: v for k, v in params.items() if k not in ['limit', 'offset']})
                total_count = count_result.scalar()
                
                search_result = {
                    'opportunities': opportunities,
                    'total_count': total_count,
                    'has_next': offset + limit < total_count,
                    'has_previous': offset > 0
                }
                
                # Cache result
                if self.db_manager.redis_client:
                    await self.db_manager.redis_client.setex(
                        cache_key, 
                        self.config.cache_ttl, 
                        json.dumps(search_result, default=str)
                    )
                
                return search_result
                
        except Exception as e:
            self.logger.error(f"Optimized search failed: {e}")
            raise
    
    async def get_analytics_data(self, date_range: int = 30) -> Dict[str, Any]:
        """Get analytics data with optimized queries"""
        try:
            cache_key = f"analytics:{date_range}"
            
            # Check cache
            if self.db_manager.redis_client:
                cached_result = await self.db_manager.redis_client.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
            
            async with self.db_manager.get_read_session() as session:
                # Use materialized view or optimized queries
                analytics_query = text("""
                    SELECT 
                        COUNT(*) as total_opportunities,
                        COUNT(CASE WHEN fo.status = 'open' THEN 1 END) as open_opportunities,
                        COUNT(CASE WHEN fo.created_at >= NOW() - INTERVAL '%s days' THEN 1 END) as recent_opportunities,
                        AVG(fo.amount_usd) as avg_amount,
                        COUNT(DISTINCT fo.organization_id) as unique_organizations,
                        COUNT(DISTINCT o.country) as countries_covered
                    FROM africa_intelligence_feed fo
                    LEFT JOIN organizations o ON fo.organization_id = o.id
                    WHERE fo.created_at >= NOW() - INTERVAL '%s days'
                """ % (date_range, date_range))
                
                result = await session.execute(analytics_query)
                analytics = dict(result.fetchone())
                
                # Cache for longer period
                if self.db_manager.redis_client:
                    await self.db_manager.redis_client.setex(
                        cache_key, 
                        self.config.cache_ttl * 4,  # 20 minutes
                        json.dumps(analytics, default=str)
                    )
                
                return analytics
                
        except Exception as e:
            self.logger.error(f"Analytics query failed: {e}")
            raise

# =============================================================================
# DATABASE INDEXES AND OPTIMIZATION
# =============================================================================

class DatabaseOptimizer:
    """Database optimization utilities"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    async def create_optimized_indexes(self):
        """Create optimized database indexes"""
        try:
            async with self.db_manager.get_session() as session:
                # Index definitions
                indexes = [
                    # Full-text search index
                    "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_search ON africa_intelligence_feed USING gin(search_vector)",
                    
                    # Composite indexes for common queries
                    "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_status_deadline ON africa_intelligence_feed(status, deadline)",
                    "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_amount_status ON africa_intelligence_feed(amount_usd, status)",
                    "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_org_created ON africa_intelligence_feed(organization_id, created_at DESC)",
                    
                    # Validation indexes
                    "CREATE INDEX IF NOT EXISTS idx_validation_results_status ON validation_results(status)",
                    "CREATE INDEX IF NOT EXISTS idx_validation_results_confidence ON validation_results(confidence_score DESC)",
                    
                    # Organization indexes
                    "CREATE INDEX IF NOT EXISTS idx_organizations_country ON organizations(country)",
                    "CREATE INDEX IF NOT EXISTS idx_organizations_type ON organizations(type)",
                    
                    # Partial indexes for common filters
                    "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_open ON africa_intelligence_feed(deadline) WHERE status = 'open'",
                    "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_high_amount ON africa_intelligence_feed(amount_usd DESC) WHERE amount_usd > 10000",
                ]
                
                for index_sql in indexes:
                    await session.execute(text(index_sql))
                    
                await session.commit()
                
                self.logger.info("Database indexes created successfully")
                
        except Exception as e:
            self.logger.error(f"Index creation failed: {e}")
            raise
    
    async def create_materialized_views(self):
        """Create materialized views for common queries"""
        try:
            async with self.db_manager.get_session() as session:
                # Analytics materialized view
                analytics_view = """
                    CREATE MATERIALIZED VIEW IF NOT EXISTS mv_funding_analytics AS
                    SELECT 
                        DATE_TRUNC('day', fo.created_at) as date,
                        COUNT(*) as daily_opportunities,
                        COUNT(CASE WHEN fo.status = 'open' THEN 1 END) as open_opportunities,
                        AVG(fo.amount_usd) as avg_amount,
                        COUNT(DISTINCT fo.organization_id) as unique_organizations,
                        COUNT(DISTINCT o.country) as countries
                    FROM africa_intelligence_feed fo
                    LEFT JOIN organizations o ON fo.organization_id = o.id
                    WHERE fo.created_at >= NOW() - INTERVAL '90 days'
                    GROUP BY DATE_TRUNC('day', fo.created_at)
                    ORDER BY date DESC
                """
                
                await session.execute(text(analytics_view))
                
                # Create unique index on materialized view
                await session.execute(text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_funding_analytics_date ON mv_funding_analytics(date)"
                ))
                
                await session.commit()
                
                self.logger.info("Materialized views created successfully")
                
        except Exception as e:
            self.logger.error(f"Materialized view creation failed: {e}")
            raise
    
    async def update_table_statistics(self):
        """Update table statistics for query optimization"""
        try:
            async with self.db_manager.get_session() as session:
                await session.execute(text("ANALYZE africa_intelligence_feed"))
                await session.execute(text("ANALYZE organizations"))
                await session.execute(text("ANALYZE validation_results"))
                await session.commit()
                
                self.logger.info("Table statistics updated")
                
        except Exception as e:
            self.logger.error(f"Statistics update failed: {e}")
            raise

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_usage():
    """Example usage of database optimization"""
    config = DatabaseConfig()
    db_manager = DatabaseManager(config, "postgresql+asyncpg://user:pass@localhost/db")
    
    await db_manager.initialize()
    
    crud = OptimizedCRUD(db_manager)
    optimizer = DatabaseOptimizer(db_manager)
    
    # Create indexes
    await optimizer.create_optimized_indexes()
    
    # Example search
    search_params = {
        'keyword': 'AI funding',
        'min_amount': 10000,
        'status': 'open'
    }
    
    results = await crud.search_opportunities_optimized(search_params, limit=20)
    print(f"Found {results['total_count']} opportunities")
    
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(example_usage())