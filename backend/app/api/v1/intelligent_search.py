"""
Intelligent Search API - Filtered Vector-Based Search
Replaces deprecated RFPs endpoint with quality-filtered, vector-enhanced search
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.services.funding_intelligence.vector_intelligence import VectorSearchService
from app.models.funding import AfricaIntelligenceItem
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/intelligent-search", tags=["intelligent-search"])

class IntelligentSearchService:
    """Service for filtered, vector-enhanced search of funding opportunities"""
    
    def __init__(self):
        self.vector_service = VectorSearchService()
    
    async def search_opportunities(
        self,
        query: str,
        db: Session,
        min_relevance_score: float = 0.6,
        max_results: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        use_vector_enhancement: bool = True
    ) -> Dict[str, Any]:
        """
        Perform filtered vector search for funding opportunities
        
        Args:
            query: User search query
            db: Database session
            min_relevance_score: Minimum relevance score (from our new scoring system)
            max_results: Maximum number of results to return
            filters: Additional filters (amount, deadline, etc.)
        
        Returns:
            Filtered and ranked search results
        """
        try:
            # Step 1: Apply database-level quality filters (PRIMARY LAYER)
            quality_filtered_ids = await self._apply_quality_filters(db, filters, min_relevance_score)
            
            if not quality_filtered_ids:
                return {
                    "query": query,
                    "results": [],
                    "total_count": 0,
                    "message": "No opportunities meet the quality criteria",
                    "search_strategy": "quality_filtering_only"
                }
            
            # Step 2: Try traditional text search first (FAST PATH)
            traditional_results = await self._traditional_text_search(
                query, quality_filtered_ids, db, max_results
            )
            
            # Step 3: Use vector search as enhancement if needed (ENHANCEMENT LAYER)
            final_results = traditional_results
            search_strategy = "traditional_search"
            
            if use_vector_enhancement and len(traditional_results) < max_results // 2:
                # If traditional search yields few results, enhance with vector search
                vector_results = await self._vector_search_filtered(
                    query, quality_filtered_ids, max_results
                )
                
                # Merge and deduplicate results
                final_results = await self._merge_search_results(
                    traditional_results, vector_results, max_results
                )
                search_strategy = "hybrid_enhanced"
            
            # Step 4: Apply final ranking and formatting
            final_results = await self._rank_and_format_results(
                final_results, query
            )
            
            return {
                "query": query,
                "results": final_results,
                "total_count": len(final_results),
                "search_metadata": {
                    "quality_filtered_count": len(quality_filtered_ids),
                    "traditional_results_count": len(traditional_results),
                    "final_count": len(final_results),
                    "search_strategy": search_strategy,
                    "min_relevance_score": min_relevance_score,
                    "vector_enhancement_used": search_strategy == "hybrid_enhanced",
                    "search_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Intelligent search failed: {e}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    async def _apply_quality_filters(
        self, 
        db: Session, 
        filters: Optional[Dict[str, Any]], 
        min_relevance_score: float
    ) -> List[int]:
        """Apply database-level quality filters before vector search"""
        
        query = db.query(AfricaIntelligenceItem.id)
        
        # Core quality filters
        query = query.filter(
            and_(
                # Use our new relevance scoring system
                AfricaIntelligenceItem.relevance_score >= min_relevance_score,
                
                # Only validated/approved content
                AfricaIntelligenceItem.validation_status.in_(['approved', 'auto_approved']),
                
                # Active opportunities (not expired)
                or_(
                    AfricaIntelligenceItem.application_deadline.is_(None),
                    AfricaIntelligenceItem.application_deadline >= datetime.now()
                ),
                
                # Must have essential fields
                AfricaIntelligenceItem.title.isnot(None),
                AfricaIntelligenceItem.description.isnot(None),
                func.length(AfricaIntelligenceItem.title) >= 10,
                func.length(AfricaIntelligenceItem.description) >= 50
            )
        )
        
        # Apply user filters if provided
        if filters:
            if filters.get('min_amount'):
                query = query.filter(
                    AfricaIntelligenceItem.funding_amount >= filters['min_amount']
                )
            
            if filters.get('max_amount'):
                query = query.filter(
                    AfricaIntelligenceItem.funding_amount <= filters['max_amount']
                )
            
            if filters.get('deadline_after'):
                query = query.filter(
                    AfricaIntelligenceItem.application_deadline >= filters['deadline_after']
                )
            
            if filters.get('deadline_before'):
                query = query.filter(
                    AfricaIntelligenceItem.application_deadline <= filters['deadline_before']
                )
            
            if filters.get('funding_type'):
                query = query.filter(
                    AfricaIntelligenceItem.funding_type_id == filters['funding_type']
                )
            
            if filters.get('geographic_focus'):
                # Search in description or metadata for geographic terms
                geo_term = f"%{filters['geographic_focus']}%"
                query = query.filter(
                    or_(
                        AfricaIntelligenceItem.description.ilike(geo_term),
                        AfricaIntelligenceItem.eligibility_criteria.ilike(geo_term)
                    )
                )
        
        # Return list of IDs that meet quality criteria
        return [row.id for row in query.all()]
    
    async def _traditional_text_search(
        self, 
        query: str, 
        allowed_ids: List[int], 
        db: Session, 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Perform traditional PostgreSQL text search on quality-filtered opportunities"""
        
        # Use PostgreSQL's full-text search capabilities
        search_query = db.query(AfricaIntelligenceItem).filter(
            AfricaIntelligenceItem.id.in_(allowed_ids)
        )
        
        # Apply text search on title and description
        search_terms = query.lower().split()
        for term in search_terms:
            search_pattern = f"%{term}%"
            search_query = search_query.filter(
                or_(
                    func.lower(AfricaIntelligenceItem.title).like(search_pattern),
                    func.lower(AfricaIntelligenceItem.description).like(search_pattern),
                    func.lower(AfricaIntelligenceItem.eligibility_criteria).like(search_pattern)
                )
            )
        
        # Order by relevance score and limit results
        search_query = search_query.order_by(
            AfricaIntelligenceItem.relevance_score.desc(),
            AfricaIntelligenceItem.created_at.desc()
        ).limit(max_results)
        
        # Convert to dictionary format
        results = []
        for opportunity in search_query.all():
            result = {
                'id': opportunity.id,
                'title': opportunity.title,
                'description': opportunity.description,
                'funding_amount': opportunity.funding_amount,
                'currency': opportunity.currency,
                'application_deadline': opportunity.application_deadline.isoformat() if opportunity.application_deadline else None,
                'application_url': opportunity.application_url,
                'contact_email': opportunity.contact_email,
                'eligibility_criteria': opportunity.eligibility_criteria,
                'source_url': opportunity.source_url,
                'relevance_score': opportunity.relevance_score,
                'validation_status': opportunity.validation_status,
                'search_method': 'traditional_text',
                'created_at': opportunity.created_at.isoformat() if opportunity.created_at else None,
                'updated_at': opportunity.updated_at.isoformat() if opportunity.updated_at else None
            }
            results.append(result)
        
        return results
    
    async def _vector_search_filtered(
        self, 
        query: str, 
        allowed_ids: List[int], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Perform vector search limited to quality-filtered IDs"""
        
        # Perform semantic search
        vector_results = await self.vector_service.intelligent_opportunity_discovery(query)
        
        # Filter results to only include quality-approved IDs
        filtered_results = []
        for opportunity in vector_results.get('opportunities', []):
            opportunity_id = opportunity.get('metadata', {}).get('opportunity_id')
            if opportunity_id and int(opportunity_id) in allowed_ids:
                filtered_results.append(opportunity)
        
        # Sort by vector similarity score and limit results
        filtered_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return filtered_results[:max_results]
    
    async def _enrich_with_database_details(
        self, 
        vector_results: List[Dict[str, Any]], 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Enrich vector results with full database details"""
        
        enriched_results = []
        
        for result in vector_results:
            opportunity_id = result.get('metadata', {}).get('opportunity_id')
            if not opportunity_id:
                continue
            
            # Fetch full opportunity details from database
            opportunity = db.query(AfricaIntelligenceItem).filter(
                AfricaIntelligenceItem.id == int(opportunity_id)
            ).first()
            
            if opportunity:
                enriched_result = {
                    'id': opportunity.id,
                    'title': opportunity.title,
                    'description': opportunity.description,
                    'funding_amount': opportunity.funding_amount,
                    'currency': opportunity.currency,
                    'application_deadline': opportunity.application_deadline.isoformat() if opportunity.application_deadline else None,
                    'application_url': opportunity.application_url,
                    'contact_email': opportunity.contact_email,
                    'eligibility_criteria': opportunity.eligibility_criteria,
                    'source_url': opportunity.source_url,
                    'relevance_score': opportunity.relevance_score,
                    'validation_status': opportunity.validation_status,
                    'vector_similarity_score': result.get('score', 0),
                    'created_at': opportunity.created_at.isoformat() if opportunity.created_at else None,
                    'updated_at': opportunity.updated_at.isoformat() if opportunity.updated_at else None
                }
                enriched_results.append(enriched_result)
        
        return enriched_results
    
    async def _merge_search_results(
        self, 
        traditional_results: List[Dict[str, Any]], 
        vector_results: List[Dict[str, Any]], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Merge traditional and vector search results, avoiding duplicates"""
        
        # Create a set of IDs from traditional results to avoid duplicates
        traditional_ids = {result['id'] for result in traditional_results}
        
        # Add vector results that aren't already in traditional results
        merged_results = traditional_results.copy()
        
        for vector_result in vector_results:
            if vector_result['id'] not in traditional_ids and len(merged_results) < max_results:
                # Mark as vector-enhanced result
                vector_result['search_method'] = 'vector_enhanced'
                merged_results.append(vector_result)
        
        return merged_results[:max_results]
    
    async def _rank_and_format_results(
        self, 
        enriched_results: List[Dict[str, Any]], 
        query: str
    ) -> List[Dict[str, Any]]:
        """Apply final ranking and formatting to results"""
        
        # Calculate composite score: relevance_score + vector_similarity + urgency
        for result in enriched_results:
            relevance_score = result.get('relevance_score', 0)
            vector_score = result.get('vector_similarity_score', 0)
            
            # Urgency boost for near deadlines
            urgency_boost = 0
            if result.get('application_deadline'):
                try:
                    deadline = datetime.fromisoformat(result['application_deadline'].replace('Z', '+00:00'))
                    days_until_deadline = (deadline - datetime.now()).days
                    if 0 <= days_until_deadline <= 30:
                        urgency_boost = 0.1  # Boost for deadlines within 30 days
                    elif 0 <= days_until_deadline <= 90:
                        urgency_boost = 0.05  # Smaller boost for deadlines within 90 days
                except:
                    pass
            
            # Composite score (weighted combination)
            composite_score = (
                relevance_score * 0.4 +  # Our objective relevance scoring
                vector_score * 0.5 +     # Vector similarity to query
                urgency_boost * 0.1      # Deadline urgency
            )
            
            result['composite_score'] = composite_score
        
        # Sort by composite score
        enriched_results.sort(key=lambda x: x.get('composite_score', 0), reverse=True)
        
        return enriched_results


# Initialize service
search_service = IntelligentSearchService()

@router.get("/opportunities")
async def search_opportunities(
    q: str = Query(..., description="Search query"),
    min_relevance: float = Query(0.6, description="Minimum relevance score (0.0-1.0)"),
    max_results: int = Query(20, description="Maximum number of results"),
    min_amount: Optional[float] = Query(None, description="Minimum funding amount"),
    max_amount: Optional[float] = Query(None, description="Maximum funding amount"),
    deadline_after: Optional[str] = Query(None, description="Deadline after date (ISO format)"),
    deadline_before: Optional[str] = Query(None, description="Deadline before date (ISO format)"),
    funding_type: Optional[int] = Query(None, description="Funding type ID"),
    geographic_focus: Optional[str] = Query(None, description="Geographic focus area"),
    db: Session = Depends(get_db)
):
    """
    Intelligent search for funding opportunities using filtered vector search
    
    This endpoint replaces the deprecated /rfps/ endpoint with:
    - Quality filtering based on relevance scores
    - Vector-based semantic search
    - Composite ranking system
    - Real-time filtering capabilities
    """
    
    # Build filters dictionary
    filters = {}
    if min_amount is not None:
        filters['min_amount'] = min_amount
    if max_amount is not None:
        filters['max_amount'] = max_amount
    if deadline_after:
        try:
            filters['deadline_after'] = datetime.fromisoformat(deadline_after)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deadline_after format. Use ISO format.")
    if deadline_before:
        try:
            filters['deadline_before'] = datetime.fromisoformat(deadline_before)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deadline_before format. Use ISO format.")
    if funding_type is not None:
        filters['funding_type'] = funding_type
    if geographic_focus:
        filters['geographic_focus'] = geographic_focus
    
    # Perform intelligent search
    results = await search_service.search_opportunities(
        query=q,
        db=db,
        min_relevance_score=min_relevance,
        max_results=max_results,
        filters=filters if filters else None
    )
    
    return results

@router.get("/suggestions")
async def get_search_suggestions(
    partial_query: str = Query(..., description="Partial search query for suggestions"),
    limit: int = Query(5, description="Maximum number of suggestions")
):
    """Get search suggestions based on partial query"""
    
    # This could be enhanced with a suggestion system based on:
    # - Popular search terms
    # - Funding categories
    # - Geographic regions
    # - Common funding types
    
    suggestions = [
        "AI healthcare funding Africa",
        "fintech startup grants Kenya",
        "agricultural innovation funding",
        "women entrepreneurs grants",
        "renewable energy funding",
        "education technology grants",
        "research funding universities",
        "seed funding startups"
    ]
    
    # Simple filtering based on partial query
    filtered_suggestions = [
        s for s in suggestions 
        if partial_query.lower() in s.lower()
    ][:limit]
    
    return {
        "suggestions": filtered_suggestions,
        "partial_query": partial_query
    }
