from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import logging
from supabase import Client

from app.core.database import get_db
from app.models import AfricaIntelligenceItem, Organization, AIDomain, FundingType, GeographicScope
from app.schemas.funding import (
    AfricaIntelligenceItemResponse, AfricaIntelligenceItemCreate, AfricaIntelligenceItemUpdate,
    GrantFundingSpecific, InvestmentFundingSpecific, FundingAnnouncementCardResponse
)
from app.services.funding_intelligence.vector_intelligence import FundingIntelligenceVectorDB

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize vector database for Pinecone integration
try:
    vector_db = FundingIntelligenceVectorDB()
    logger.info("✅ Pinecone vector database initialized for funding opportunities API")
except Exception as e:
    logger.warning(f"⚠️ Failed to initialize Pinecone vector database: {e}")
    vector_db = None

#
# Core Intelligence Item Endpoints (from funding.py)
#

@router.get("/", response_model=List[FundingAnnouncementCardResponse])
async def get_africa_intelligence_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    currency: Optional[str] = "USD",
    deadline_after: Optional[datetime] = Query(None),
    deadline_before: Optional[datetime] = Query(None),
    organization_id: Optional[int] = Query(None),
    ai_domain: Optional[str] = Query(None),
    funding_type: Optional[str] = Query(None, description="Filter by funding type category: 'grant', 'investment', 'prize', or 'other'"),
    requires_equity: Optional[bool] = Query(None, description="Filter for opportunities requiring equity"),
    db = Depends(get_db)
):
    """Get intelligence feed with optional filtering, formatted for FundingAnnouncementCard"""
    # Check if db is a Supabase client or SQLAlchemy session
    query = db.table('africa_intelligence_feed').select('*, funding_types!fk_africa_intelligence_feed_funding_type_id(*), organizations!africa_intelligence_feed_organization_id_fkey(*), ai_domains!intelligence_item_ai_domains(*)')

    # Apply filters
    if status:
        query = query.filter('status', 'eq', status)
    if min_amount:
        query = query.or_(f'amount_exact.gte.{min_amount},amount_min.gte.{min_amount},total_funding_pool.gte.{min_amount}')
    if max_amount:
        query = query.or_(f'amount_exact.lte.{max_amount},amount_max.lte.{max_amount},total_funding_pool.lte.{max_amount}')
    if deadline_after:
        query = query.filter('deadline', 'gte', deadline_after.isoformat())
    if deadline_before:
        query = query.filter('deadline', 'lte', deadline_before.isoformat())
    if organization_id:
        query = query.filter('organization_id', 'eq', organization_id)
    if funding_type:
        query = query.filter('funding_types.category', 'eq', funding_type)
    if requires_equity is not None:
        query = query.filter('funding_types.requires_equity', 'eq', requires_equity)
    if ai_domain:
        query = query.filter('ai_domains.name', 'ilike', f'%{ai_domain}%')

    # Execute query with pagination
    response = query.range(skip, skip + limit - 1).execute()
    opportunities = response.data
    
    # Prepare responses with type-specific data
    results = []
    for opp in opportunities:
        # Handle organization info
        organization_data = opp.get('organizations', {})
        organization_name = organization_data.get('name') if organization_data else opp.get('organization_name', 'Unknown')
        
        # Handle AI domains
        ai_domains = opp.get('ai_domains', [])
        ai_domain_names = [domain.get('name') for domain in ai_domains if domain.get('name')]
        
        # Handle funding type data
        funding_type_data = opp.get('funding_types', {})
        funding_category = funding_type_data.get('category', 'other')
        
        # Prepare response data for FundingAnnouncementCard
        response_data = {
            # Core fields
            "id": opp.get("id"),
            "title": opp.get("title"),
            "description": opp.get("description"),
            "organization": organization_name,
            "details_url": opp.get("source_url"),
            "sector": ai_domain_names[0] if ai_domain_names else "Other",
            "country": opp.get("country", "Multiple"),
            "region": opp.get("region"),
            "deadline": opp.get("deadline"),
            "status": opp.get("status", "open"),
            
            # Enhanced funding fields
            "total_funding_pool": float(opp.get("total_funding_pool")) if opp.get("total_funding_pool") is not None else None,
            "funding_type": opp.get("funding_type", "per_project_range"),
            "min_amount_per_project": float(opp.get("min_amount_per_project")) if opp.get("min_amount_per_project") is not None else None,
            "max_amount_per_project": float(opp.get("max_amount_per_project")) if opp.get("max_amount_per_project") is not None else None,
            "exact_amount_per_project": float(opp.get("exact_amount_per_project")) if opp.get("exact_amount_per_project") is not None else None,
            "estimated_project_count": opp.get("estimated_project_count"),
            "project_count_range": opp.get("project_count_range"),
            "currency": opp.get("currency", "USD"),
            
            # Application & process information
            "application_process": opp.get("application_process"),
            "selection_criteria": opp.get("selection_criteria") or [],
            "application_deadline_type": opp.get("application_deadline_type", "fixed"),
            "announcement_date": opp.get("announcement_date"),
            "start_date": opp.get("start_date"),
            "funding_start_date": opp.get("funding_start_date"),
            "project_duration": opp.get("project_duration"),
            "status": opp.get("status"),
            
            # Enhanced application and selection process
            "application_process": opp.get("application_process"),
            "selection_criteria": opp.get("selection_criteria"),
            
            # Contact and URLs
            "source_url": opp.get("source_url"),
            "application_url": opp.get("application_url"),
            "contact_info": opp.get("contact_info"),
            "geographical_scope": opp.get("geographical_scope"),
            "eligibility_criteria": opp.get("eligibility_criteria"),
            "application_deadline": opp.get("application_deadline"),
            "max_funding_period_months": opp.get("max_funding_period_months"),
            
            # Enhanced targeting and focus areas
            "target_audience": opp.get("target_audience"),
            "ai_subsectors": opp.get("ai_subsectors"),
            "development_stage": opp.get("development_stage"),
            "collaboration_required": opp.get("collaboration_required"),
            "gender_focused": opp.get("gender_focused"),
            "youth_focused": opp.get("youth_focused"),
            "reporting_requirements": opp.get("reporting_requirements"),
            
            # Metadata
            "created_at": opp.get("created_at"),
            "updated_at": opp.get("updated_at"),
            "last_checked": opp.get("last_checked"),
            "source_organization": opp.get("source_organization"),
            "provider_organization": opp.get("provider_organization"),
            "recipient_organization": opp.get("recipient_organization"),
            "ai_domains": opp.get("ai_domains", []),
            "funding_type": funding_type_data,
            "is_grant": is_grant,
            "is_investment": is_investment,
            "funding_category": funding_category
        }

        # Add type-specific data if available
        grant_specific = {}
        if is_grant:
            if opp.get("reporting_requirements"):
                grant_specific["reporting_requirements"] = opp["reporting_requirements"]
            if opp.get("grant_duration_months"):
                grant_specific["grant_duration_months"] = opp["grant_duration_months"]
            if opp.get("renewable") is not None:
                grant_specific["renewable"] = opp["renewable"]
            if opp.get("no_strings_attached") is not None:
                grant_specific["no_strings_attached"] = opp["no_strings_attached"]
            if opp.get("project_based") is not None:
                grant_specific["project_based"] = opp["project_based"]
            if grant_specific:
                response_data["grant_specific"] = GrantFundingSpecific(**grant_specific)

        investment_specific = {}
        if is_investment:
            if opp.get("equity_percentage"):
                investment_specific["equity_percentage"] = opp["equity_percentage"]
            if opp.get("valuation_cap"):
                investment_specific["valuation_cap"] = opp["valuation_cap"]
            if opp.get("interest_rate"):
                investment_specific["interest_rate"] = opp["interest_rate"]
            if opp.get("repayment_terms"):
                investment_specific["repayment_terms"] = opp["repayment_terms"]
            if opp.get("investor_rights"):
                investment_specific["investor_rights"] = opp["investor_rights"]
            if opp.get("post_investment_support"):
                investment_specific["post_investment_support"] = opp["post_investment_support"]
            if opp.get("expected_roi"):
                investment_specific["expected_roi"] = opp["expected_roi"]
            if investment_specific:
                response_data["investment_specific"] = InvestmentFundingSpecific(**investment_specific)

        results.append(AfricaIntelligenceItemResponse(**response_data))
    
    return results


@router.get("/{opportunity_id}", response_model=AfricaIntelligenceItemResponse)
async def get_intelligence_item(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific intelligence item by ID"""
    opportunity = db.query(AfricaIntelligenceItem).filter(AfricaIntelligenceItem.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")
    
    # Prepare response with type-specific data
    if hasattr(db, 'table'): # Supabase client
        # Extract funding_type details
        funding_type_data = opportunity.get('funding_types')
        funding_category = funding_type_data.get('category', 'other') if funding_type_data else 'other'
        is_grant = funding_category == 'grant'
        is_investment = funding_category == 'investment'

        # Prepare base data for response
        response_data = {
            "id": opportunity.get("id"),
            "title": opportunity.get("title"),
            "description": opportunity.get("description"),
            "amount": opportunity.get("amount"),
            "amount_min": opportunity.get("amount_min"),
            "amount_max": opportunity.get("amount_max"),
            "amount_exact": opportunity.get("amount_exact"),
            "currency": opportunity.get("currency"),
            "amount_usd": opportunity.get("amount_usd"),
            "deadline": opportunity.get("deadline"),
            "announcement_date": opportunity.get("announcement_date"),
            "start_date": opportunity.get("start_date"),
            "status": opportunity.get("status"),
            "source_url": opportunity.get("source_url"),
            "application_url": opportunity.get("application_url"),
            "contact_info": opportunity.get("contact_info"),
            "geographical_scope": opportunity.get("geographical_scope"),
            "eligibility_criteria": opportunity.get("eligibility_criteria"),
            "application_deadline": opportunity.get("application_deadline"),
            "max_funding_period_months": opportunity.get("max_funding_period_months"),
            "created_at": opportunity.get("created_at"),
            "updated_at": opportunity.get("updated_at"),
            "last_checked": opportunity.get("last_checked"),
            "source_organization": opportunity.get("source_organization"),
            "provider_organization": opportunity.get("provider_organization"),
            "recipient_organization": opportunity.get("recipient_organization"),
            "ai_domains": opportunity.get("ai_domains", []),
            "funding_type": funding_type_data,
            "is_grant": is_grant,
            "is_investment": is_investment,
            "funding_category": funding_category
        }

        # Add type-specific data if available
        grant_specific = {}
        if is_grant:
            if opportunity.get("reporting_requirements"):
                grant_specific["reporting_requirements"] = opportunity["reporting_requirements"]
            if opportunity.get("grant_duration_months"):
                grant_specific["grant_duration_months"] = opportunity["grant_duration_months"]
            if opportunity.get("renewable") is not None:
                grant_specific["renewable"] = opportunity["renewable"]
            if opportunity.get("no_strings_attached") is not None:
                grant_specific["no_strings_attached"] = opportunity["no_strings_attached"]
            if opportunity.get("project_based") is not None:
                grant_specific["project_based"] = opportunity["project_based"]
            if grant_specific:
                response_data["grant_specific"] = GrantFundingSpecific(**grant_specific)

        investment_specific = {}
        if is_investment:
            if opportunity.get("equity_percentage"):
                investment_specific["equity_percentage"] = opportunity["equity_percentage"]
            if opportunity.get("valuation_cap"):
                investment_specific["valuation_cap"] = opportunity["valuation_cap"]
            if opportunity.get("interest_rate"):
                investment_specific["interest_rate"] = opportunity["interest_rate"]
            if opportunity.get("repayment_terms"):
                investment_specific["repayment_terms"] = opportunity["repayment_terms"]
            if opportunity.get("investor_rights"):
                investment_specific["investor_rights"] = opportunity["investor_rights"]
            if opportunity.get("post_investment_support"):
                investment_specific["post_investment_support"] = opportunity["post_investment_support"]
            if opportunity.get("expected_roi"):
                investment_specific["expected_roi"] = opportunity["expected_roi"]
            if investment_specific:
                response_data["investment_specific"] = InvestmentFundingSpecific(**investment_specific)

        response = AfricaIntelligenceItemResponse(**response_data)
    else: # SQLAlchemy session
        response = AfricaIntelligenceItemResponse.from_orm(opportunity)
        
        # Add type-specific data
        response.is_grant = opportunity.is_grant
        response.is_investment = opportunity.is_investment
        response.funding_category = opportunity.funding_category
        
        if opportunity.is_grant and opportunity.grant_properties:
            response.grant_specific = GrantFundingSpecific(**opportunity.grant_properties)
        
        if opportunity.is_investment and opportunity.investment_properties:
            response.investment_specific = InvestmentFundingSpecific(**opportunity.investment_properties)
    
    return response


@router.post("/", response_model=AfricaIntelligenceItemResponse)
async def create_intelligence_item(
    opportunity: AfricaIntelligenceItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new intelligence item"""
    if hasattr(db, 'table'): # Supabase client
        # Validate the funding type exists and get its category
        funding_type_response = db.table('funding_types').select('*').eq('id', opportunity.funding_type_id).execute()
        funding_type_data = funding_type_response.data[0] if funding_type_response.data else None
        if not funding_type_data:
            raise HTTPException(status_code=404, detail="Funding type not found")
        
        # Prepare base opportunity data
        opportunity_dict = opportunity.model_dump(exclude_unset=True, exclude={"grant_specific", "investment_specific"})
        # Ensure funding_type_id is included (table has both type_id and funding_type_id)
        opportunity_dict['funding_type_id'] = opportunity.funding_type_id
        opportunity_dict['created_at'] = datetime.utcnow().isoformat()

        # Add type-specific fields based on funding type category
        if funding_type_data['category'] == 'grant' and opportunity.grant_specific:
            grant_data = opportunity.grant_specific.dict(exclude_unset=True)
            opportunity_dict.update(grant_data)
        
        if funding_type_data['category'] == 'investment' and opportunity.investment_specific:
            investment_data = opportunity.investment_specific.dict(exclude_unset=True)
            opportunity_dict.update(investment_data)
        
        # Insert into Supabase
        logger.info("Inserting opportunity into Supabase...")
        insert_response = db.table('africa_intelligence_feed').insert(opportunity_dict).execute()
        
        # Check if the insert was successful
        if hasattr(insert_response, 'data') and insert_response.data:
            # If the insert returns the data, use it
            db_opportunity = insert_response.data[0] if isinstance(insert_response.data, list) else insert_response.data
            logger.info(f"✅ Successfully inserted opportunity. ID: {db_opportunity.get('id')}")
        else:
            # If insert didn't return the data, try to fetch the most recent record
            logger.info("Insert response didn't contain data. Trying to fetch most recent record...")
            try:
                recent = db.table('africa_intelligence_feed')\
                         .select('*')\
                         .order('created_at', desc=True)\
                         .limit(1)\
                         .execute()
                
                if recent.data:
                    db_opportunity = recent.data[0]
                    logger.info(f"✅ Retrieved recently inserted record with fallback query. ID: {db_opportunity.get('id')}")
                else:
                    logger.error("❌ No records found in the table after insert")
                    raise HTTPException(status_code=500, detail="Failed to create opportunity in Supabase")
            except Exception as e:
                logger.error(f"❌ Fallback query failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to create or retrieve opportunity")

        # Prepare response with type-specific data
        funding_category = funding_type_data.get('category', 'other')
        is_grant = funding_category == 'grant'
        is_investment = funding_category == 'investment'

        # Ensure we have a valid ID
        item_id = db_opportunity.get('id')
        if item_id is None:
            raise HTTPException(status_code=500, detail="Database did not return an ID for the created item")

        # 🔥 ADD PINECONE VECTOR INDEXING 🔥
        # Index the new opportunity in Pinecone for semantic search
        if vector_db:
            try:
                # Prepare data for Pinecone indexing
                pinecone_data = {
                    'id': str(item_id),
                    'title': db_opportunity.get('title', ''),
                    'description': db_opportunity.get('description', ''),
                    'funding_type': funding_type_data.get('name', ''),
                    'funding_category': funding_category,
                    'amount_min': db_opportunity.get('amount_min'),
                    'amount_max': db_opportunity.get('amount_max'),
                    'amount_exact': db_opportunity.get('amount_exact'),
                    'currency': db_opportunity.get('currency', 'USD'),
                    'geographical_scope': db_opportunity.get('geographical_scope', ''),
                    'eligibility_criteria': db_opportunity.get('eligibility_criteria', ''),
                    'source_url': db_opportunity.get('source_url', ''),
                    'application_url': db_opportunity.get('application_url', ''),
                    'deadline': db_opportunity.get('deadline'),
                    'status': db_opportunity.get('status', 'open'),
                    'created_at': db_opportunity.get('created_at')
                }
                
                # Index to Pinecone asynchronously
                await vector_db.upsert_intelligence_item(pinecone_data)
                logger.info(f"✅ Successfully indexed opportunity {item_id} to Pinecone")
                
            except Exception as e:
                # Don't fail the API call if Pinecone indexing fails
                logger.error(f"❌ Failed to index opportunity {item_id} to Pinecone: {e}")
                # Continue with the response even if Pinecone fails

        response_data = {
            **db_opportunity,
            "id": item_id,
            "funding_type_id": opportunity.funding_type_id,
            "funding_type": funding_type_data,
            "is_grant": is_grant,
            "is_investment": is_investment,
            "funding_category": funding_category
        }

        if is_grant and opportunity.grant_specific:
            response_data["grant_specific"] = opportunity.grant_specific
        if is_investment and opportunity.investment_specific:
            response_data["investment_specific"] = opportunity.investment_specific

        return AfricaIntelligenceItemResponse(**response_data)

    else: # SQLAlchemy session
        # Validate the funding type exists and get its category
        funding_type = db.query(FundingType).filter(FundingType.id == opportunity.funding_type_id).first()
        if not funding_type:
            raise HTTPException(status_code=404, detail="Funding type not found")
        
        # Prepare base opportunity data
        opportunity_data = opportunity.dict(exclude={"grant_specific", "investment_specific"})
        db_opportunity = AfricaIntelligenceItem(**opportunity_data)
        
        # Add type-specific fields based on funding type category
        if funding_type.category == 'grant' and opportunity.grant_specific:
            grant_data = opportunity.grant_specific.dict()
            for key, value in grant_data.items():
                if value is not None:  # Only set non-None values
                    setattr(db_opportunity, key, value)
        
        if funding_type.category == 'investment' and opportunity.investment_specific:
            investment_data = opportunity.investment_specific.dict()
            for key, value in investment_data.items():
                if value is not None:  # Only set non-None values
                    setattr(db_opportunity, key, value)
        
        db.add(db_opportunity)
        db.commit()
        db.refresh(db_opportunity)
        
        # 🔥 ADD PINECONE VECTOR INDEXING FOR SQLALCHEMY 🔥
        if vector_db:
            try:
                # Prepare data for Pinecone indexing
                pinecone_data = {
                    'id': str(db_opportunity.id),
                    'title': db_opportunity.title or '',
                    'description': db_opportunity.description or '',
                    'funding_type': funding_type.name,
                    'funding_category': funding_type.category,
                    'amount_min': db_opportunity.amount_min,
                    'amount_max': db_opportunity.amount_max,
                    'amount_exact': db_opportunity.amount_exact,
                    'currency': db_opportunity.currency or 'USD',
                    'geographical_scope': db_opportunity.geographical_scope or '',
                    'eligibility_criteria': db_opportunity.eligibility_criteria or '',
                    'source_url': db_opportunity.source_url or '',
                    'application_url': db_opportunity.application_url or '',
                    'deadline': db_opportunity.deadline,
                    'status': db_opportunity.status or 'open',
                    'created_at': db_opportunity.created_at
                }
                
                # Index to Pinecone asynchronously
                await vector_db.upsert_intelligence_item(pinecone_data)
                logger.info(f"✅ Successfully indexed opportunity {db_opportunity.id} to Pinecone")
                
            except Exception as e:
                # Don't fail the API call if Pinecone indexing fails
                logger.error(f"❌ Failed to index opportunity {db_opportunity.id} to Pinecone: {e}")
        
        # Create response with type-specific data
        response = AfricaIntelligenceItemResponse.from_orm(db_opportunity)
        response.is_grant = db_opportunity.is_grant
        response.is_investment = db_opportunity.is_investment
        response.funding_category = db_opportunity.funding_category
        
        if db_opportunity.is_grant and db_opportunity.grant_properties:
            response.grant_specific = GrantFundingSpecific(**db_opportunity.grant_properties)
        
        if db_opportunity.is_investment and db_opportunity.investment_properties:
            response.investment_specific = InvestmentFundingSpecific(**db_opportunity.investment_properties)
        
        return response


@router.get("/grants/", response_model=List[AfricaIntelligenceItemResponse])
async def get_grants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    renewable: Optional[bool] = Query(None, description="Filter for renewable grants"),
    project_based: Optional[bool] = Query(None, description="Filter for project-based grants"),
    min_duration: Optional[int] = Query(None, description="Minimum grant duration in months"),
    db: AsyncSession = Depends(get_db)
):
    """Get grant intelligence feed with specialized filters"""
    if hasattr(db, 'table'): # Supabase client
        query = db.table('africa_intelligence_feed').select('*, funding_types!fk_africa_intelligence_feed_funding_type_id(*)')
        
        # Filter by grant type
        query = query.filter('funding_types.category', 'eq', 'grant')
        
        # Apply specialized grant filters
        if renewable is not None:
            query = query.filter('renewable', 'eq', renewable)
        if project_based is not None:
            query = query.filter('project_based', 'eq', project_based)
        if min_duration is not None:
            query = query.filter('grant_duration_months', 'gte', min_duration)
        
        # Execute query with pagination
        response = query.range(skip, skip + limit - 1).execute()
        grants = response.data
        
        # Prepare responses with type-specific data
        results = []
        for grant in grants:
            funding_type_data = grant.get('funding_types')
            funding_category = funding_type_data.get('category', 'other') if funding_type_data else 'other'
            is_grant = funding_category == 'grant'
            is_investment = funding_category == 'investment'

            response_data = {
                **grant,
                "funding_type": funding_type_data,
                "is_grant": is_grant,
                "is_investment": is_investment,
                "funding_category": funding_category
            }
            if is_grant:
                grant_specific = {}
                if grant.get("reporting_requirements"):
                    grant_specific["reporting_requirements"] = grant["reporting_requirements"]
                if grant.get("grant_duration_months"):
                    grant_specific["grant_duration_months"] = grant["grant_duration_months"]
                if grant.get("renewable") is not None:
                    grant_specific["renewable"] = grant["renewable"]
                if grant.get("no_strings_attached") is not None:
                    grant_specific["no_strings_attached"] = grant["no_strings_attached"]
                if grant.get("project_based") is not None:
                    grant_specific["project_based"] = grant["project_based"]
                if grant_specific:
                    response_data["grant_specific"] = GrantFundingSpecific(**grant_specific)
            results.append(AfricaIntelligenceItemResponse(**response_data))
        
        return results

    else: # SQLAlchemy session
        query = db.query(AfricaIntelligenceItem).join(AfricaIntelligenceItem.type)
        
        # Filter by grant type
        query = query.filter(FundingType.category == 'grant')
        
        # Apply specialized grant filters
        if renewable is not None:
            query = query.filter(AfricaIntelligenceItem.renewable == renewable)
        if project_based is not None:
            query = query.filter(AfricaIntelligenceItem.project_based == project_based)
        if min_duration is not None:
            query = query.filter(AfricaIntelligenceItem.grant_duration_months >= min_duration)
        
        # Execute query with pagination
        grants = query.offset(skip).limit(limit).all()
        
        # Prepare responses with type-specific data
        results = []
        for grant in grants:
            response = AfricaIntelligenceItemResponse.from_orm(grant)
            response.is_grant = True
            response.is_investment = False
            response.funding_category = 'grant'
            
            if grant.grant_properties:
                response.grant_specific = GrantFundingSpecific(**grant.grant_properties)
            
            results.append(response)
        
        return results


@router.get("/investments/", response_model=List[AfricaIntelligenceItemResponse])
async def get_investments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    max_equity: Optional[float] = Query(None, description="Maximum equity percentage required"),
    min_valuation_cap: Optional[float] = Query(None, description="Minimum valuation cap"),
    db: AsyncSession = Depends(get_db)
):
    """Get investment intelligence feed with specialized filters"""
    if hasattr(db, 'table'): # Supabase client
        query = db.table('africa_intelligence_feed').select('*, funding_types!fk_africa_intelligence_feed_funding_type_id(*)')
        
        # Filter by investment type
        query = query.filter('funding_types.category', 'eq', 'investment')
        
        # Apply specialized investment filters
        if max_equity is not None:
            query = query.filter('equity_percentage', 'lte', max_equity)
        if min_valuation_cap is not None:
            query = query.filter('valuation_cap', 'gte', min_valuation_cap)
        
        # Execute query with pagination
        response = query.range(skip, skip + limit - 1).execute()
        investments = response.data
        
        # Prepare responses with type-specific data
        results = []
        for investment in investments:
            funding_type_data = investment.get('funding_types')
            funding_category = funding_type_data.get('category', 'other') if funding_type_data else 'other'
            is_grant = funding_category == 'grant'
            is_investment = funding_category == 'investment'

            response_data = {
                **investment,
                "funding_type": funding_type_data,
                "is_grant": is_grant,
                "is_investment": is_investment,
                "funding_category": funding_category
            }
            if is_investment:
                investment_specific = {}
                if investment.get("equity_percentage"):
                    investment_specific["equity_percentage"] = investment["equity_percentage"]
                if investment.get("valuation_cap"):
                    investment_specific["valuation_cap"] = investment["valuation_cap"]
                if investment.get("interest_rate"):
                    investment_specific["interest_rate"] = investment["interest_rate"]
                if investment.get("repayment_terms"):
                    investment_specific["repayment_terms"] = investment["repayment_terms"]
                if investment.get("investor_rights"):
                    investment_specific["investor_rights"] = investment["investor_rights"]
                if investment.get("post_investment_support"):
                    investment_specific["post_investment_support"] = investment["post_investment_support"]
                if investment.get("expected_roi"):
                    investment_specific["expected_roi"] = investment["expected_roi"]
                if investment_specific:
                    response_data["investment_specific"] = InvestmentFundingSpecific(**investment_specific)
            results.append(AfricaIntelligenceItemResponse(**response_data))
        
        return results

    else: # SQLAlchemy session
        query = db.query(AfricaIntelligenceItem).join(AfricaIntelligenceItem.type)
        
        # Filter by investment type
        query = query.filter(FundingType.category == 'investment')
        
        # Apply specialized investment filters
        if max_equity is not None:
            query = query.filter(AfricaIntelligenceItem.equity_percentage <= max_equity)
        if min_valuation_cap is not None:
            query = query.filter(AfricaIntelligenceItem.valuation_cap >= min_valuation_cap)
        
        # Execute query with pagination
        investments = query.offset(skip).limit(limit).all()
        
        # Prepare responses with type-specific data
        results = []
        for investment in investments:
            response = AfricaIntelligenceItemResponse.from_orm(investment)
            response.is_grant = False
            response.is_investment = True
            response.funding_category = 'investment'
            
            if investment.investment_properties:
                response.investment_specific = InvestmentFundingSpecific(**investment.investment_properties)
            
            results.append(response)
        
        return results


@router.get("/search/", response_model=List[AfricaIntelligenceItemResponse])
async def search_africa_intelligence_feed(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    funding_type: Optional[str] = Query(None, description="Limit search to specific funding type: 'grant', 'investment', etc."),
    db: AsyncSession = Depends(get_db)
):
    """Search intelligence feed by title or description"""
    if hasattr(db, 'table'):  # Supabase client
        query = db.table('africa_intelligence_feed').select('*, funding_types!fk_africa_intelligence_feed_funding_type_id(*)')
        
        # Apply search filter
        search_term = f"%{q}%"
        query = query.or_(f'title.ilike.{search_term},description.ilike.{search_term}')

        # Apply funding type filter if specified
        if funding_type:
            query = query.filter('funding_types.category', 'eq', funding_type)

        response = query.limit(limit).execute()
        opportunities = response.data
    else:  # SQLAlchemy session
        search_term = f"%{q}%"
        query = db.query(AfricaIntelligenceItem)
        
        # Apply search filter
        query = query.filter(
            AfricaIntelligenceItem.title.ilike(search_term) | 
            AfricaIntelligenceItem.description.ilike(search_term)
        )
        
        # Apply funding type filter if specified
        if funding_type:
            query = query.join(AfricaIntelligenceItem.type)
            query = query.filter(FundingType.category == funding_type)
        
        opportunities = query.limit(limit).all()
    
    # Prepare responses with type-specific data
    results = []
    for opp in opportunities:
        # Extract funding_type details
        funding_type_data = opp.get('funding_types')
        funding_category = funding_type_data.get('category', 'other') if funding_type_data else 'other'
        is_grant = funding_category == 'grant'
        is_investment = funding_category == 'investment'

        # Prepare base data for response
        response_data = {
            "id": opp.get("id"),
            "title": opp.get("title"),
            "description": opp.get("description"),
            "amount": opp.get("amount"),
            
            # Enhanced funding fields
            "total_funding_pool": opp.get("total_funding_pool"),
            "funding_type": opp.get("funding_type", "per_project_range"),
            "min_amount_per_project": opp.get("min_amount_per_project"),
            "max_amount_per_project": opp.get("max_amount_per_project"),
            "exact_amount_per_project": opp.get("exact_amount_per_project"),
            "estimated_project_count": opp.get("estimated_project_count"),
            "project_count_range": opp.get("project_count_range"),
            
            # Legacy amount fields for backward compatibility
            "amount_min": opp.get("amount_min"),
            "amount_max": opp.get("amount_max"),
            "amount_exact": opp.get("amount_exact"),
            "currency": opp.get("currency"),
            "amount_usd": opp.get("amount_usd"),
            
            # Enhanced timing and process fields
            "deadline": opp.get("deadline"),
            "application_deadline_type": opp.get("application_deadline_type", "fixed"),
            "announcement_date": opp.get("announcement_date"),
            "start_date": opp.get("start_date"),
            "funding_start_date": opp.get("funding_start_date"),
            "project_duration": opp.get("project_duration"),
            "status": opp.get("status"),
            
            # Enhanced application and selection process
            "application_process": opp.get("application_process"),
            "selection_criteria": opp.get("selection_criteria"),
            
            # Contact and URLs
            "source_url": opp.get("source_url"),
            "application_url": opp.get("application_url"),
            "contact_info": opp.get("contact_info"),
            "geographical_scope": opp.get("geographical_scope"),
            "eligibility_criteria": opp.get("eligibility_criteria"),
            "application_deadline": opp.get("application_deadline"),
            "max_funding_period_months": opp.get("max_funding_period_months"),
            
            # Enhanced targeting and focus areas
            "target_audience": opp.get("target_audience"),
            "ai_subsectors": opp.get("ai_subsectors"),
            "development_stage": opp.get("development_stage"),
            "collaboration_required": opp.get("collaboration_required"),
            "gender_focused": opp.get("gender_focused"),
            "youth_focused": opp.get("youth_focused"),
            "reporting_requirements": opp.get("reporting_requirements"),
            
            # Metadata
            "created_at": opp.get("created_at"),
            "updated_at": opp.get("updated_at"),
            "last_checked": opp.get("last_checked"),
            "source_organization": opp.get("source_organization"),
            "provider_organization": opp.get("provider_organization"),
            "recipient_organization": opp.get("recipient_organization"),
            "ai_domains": opp.get("ai_domains", []),
            "funding_type": funding_type_data,
            "is_grant": is_grant,
            "is_investment": is_investment,
            "funding_category": funding_category
        }

        # Add type-specific data if available
        grant_specific = {}
        if is_grant:
            if opp.get("reporting_requirements"):
                grant_specific["reporting_requirements"] = opp["reporting_requirements"]
            if opp.get("grant_duration_months"):
                grant_specific["grant_duration_months"] = opp["grant_duration_months"]
            if opp.get("renewable") is not None:
                grant_specific["renewable"] = opp["renewable"]
            if opp.get("no_strings_attached") is not None:
                grant_specific["no_strings_attached"] = opp["no_strings_attached"]
            if opp.get("project_based") is not None:
                grant_specific["project_based"] = opp["project_based"]
            if grant_specific:
                response_data["grant_specific"] = GrantFundingSpecific(**grant_specific)

        investment_specific = {}
        if is_investment:
            if opp.get("equity_percentage"):
                investment_specific["equity_percentage"] = opp["equity_percentage"]
            if opp.get("valuation_cap"):
                investment_specific["valuation_cap"] = opp["valuation_cap"]
            if opp.get("interest_rate"):
                investment_specific["interest_rate"] = opp["interest_rate"]
            if opp.get("repayment_terms"):
                investment_specific["repayment_terms"] = opp["repayment_terms"]
            if opp.get("investor_rights"):
                investment_specific["investor_rights"] = opp["investor_rights"]
            if opp.get("post_investment_support"):
                investment_specific["post_investment_support"] = opp["post_investment_support"]
            if opp.get("expected_roi"):
                investment_specific["expected_roi"] = opp["expected_roi"]
            if investment_specific:
                response_data["investment_specific"] = InvestmentFundingSpecific(**investment_specific)

        results.append(AfricaIntelligenceItemResponse(**response_data))
    
    return results


#
# Stage Matching Endpoints (from opportunities.py)
#

@router.get("/stage-matching")
async def get_stage_matched_opportunities(
    stage: str = Query(None, description="Funding stage to match (e.g., 'Pre-seed', 'Seed', 'Series A')"),
    domain: str = Query(None, description="AI domain to filter by"),
    country: str = Query(None, description="Country to filter by"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get intelligence feed matched to a specific stage and optionally filtered by domain and country.
    This endpoint helps founders find opportunities appropriate for their current funding stage.
    """
    # In a real implementation, this would query the database based on the parameters
    # For demo purposes, we'll return representative stage-appropriate opportunities
    
    stages = ["Pre-seed", "Seed", "Series A", "Series B", "Series C+"]
    if stage and stage not in stages:
        return {"error": f"Invalid stage. Must be one of: {', '.join(stages)}"}
    
    # Default to seed if no stage specified
    current_stage = stage or "Seed"
    
    # Match opportunities based on stage
    if current_stage == "Pre-seed":
        opportunities = [
            {
                "id": 101,
                "title": "African Innovation Challenge",
                "organization": "African Development Bank",
                "funding_amount": "Up to $25,000",
                "deadline": "2024-08-15",
                "stage_appropriate": True,
                "requirements": "Idea stage, proof of concept",
                "success_rate": "15%",
                "application_complexity": "Low"
            },
            {
                "id": 102,
                "title": "AI for Good Incubator",
                "organization": "Google for Startups Africa",
                "funding_amount": "Up to $15,000",
                "deadline": "2024-09-01",
                "stage_appropriate": True,
                "requirements": "MVP or proof of concept",
                "success_rate": "8%",
                "application_complexity": "Medium"
            },
            {
                "id": 103,
                "title": "Women in AI Entrepreneurship Grant",
                "organization": "UN Women",
                "funding_amount": "Up to $20,000",
                "deadline": "2024-10-30",
                "stage_appropriate": True,
                "requirements": "Female-led ventures, idea stage acceptable",
                "success_rate": "12%",
                "application_complexity": "Medium"
            }
        ]
    elif current_stage == "Seed":
        opportunities = [
            {
                "id": 201,
                "title": "Africa AI Accelerator Program",
                "organization": "Microsoft 4Afrika",
                "funding_amount": "$50,000 - $150,000",
                "deadline": "2024-08-30",
                "stage_appropriate": True,
                "requirements": "Working product, some traction",
                "success_rate": "10%",
                "application_complexity": "High"
            },
            {
                "id": 202,
                "title": "Tech for Climate Action Fund",
                "organization": "World Bank Climate Initiative",
                "funding_amount": "Up to $100,000",
                "deadline": "2024-09-15",
                "stage_appropriate": True,
                "requirements": "Product with climate impact potential",
                "success_rate": "7%",
                "application_complexity": "Very High"
            },
            {
                "id": 203,
                "title": "Catalytic Africa Fund",
                "organization": "AfriLabs",
                "funding_amount": "$75,000 - $200,000",
                "deadline": "2024-11-01",
                "stage_appropriate": True,
                "requirements": "Product with early traction, revenue preferred",
                "success_rate": "5%",
                "application_complexity": "High"
            }
        ]
    elif current_stage == "Series A":
        opportunities = [
            {
                "id": 301,
                "title": "Africa Growth Fund",
                "organization": "IFC Ventures",
                "funding_amount": "$500,000 - $2M",
                "deadline": "2024-10-15",
                "stage_appropriate": True,
                "requirements": "Proven revenue model, market traction",
                "success_rate": "3%",
                "application_complexity": "Very High"
            },
            {
                "id": 302,
                "title": "AI for Development Impact Fund",
                "organization": "Bill & Melinda Gates Foundation",
                "funding_amount": "$750,000 - $1.5M",
                "deadline": "2024-09-30",
                "stage_appropriate": True,
                "requirements": "Clear impact metrics, scaling plan",
                "success_rate": "2%",
                "application_complexity": "Very High"
            }
        ]
    elif current_stage == "Series B":
        opportunities = [
            {
                "id": 401,
                "title": "Africa Scale-Up Fund",
                "organization": "Softbank Africa",
                "funding_amount": "$3M - $10M",
                "deadline": "2024-12-01",
                "stage_appropriate": True,
                "requirements": "Significant revenue, expanding market share",
                "success_rate": "1.5%",
                "application_complexity": "Extremely High"
            }
        ]
    else:  # Series C+
        opportunities = [
            {
                "id": 501,
                "title": "African Growth Champions",
                "organization": "Africa Development Bank",
                "funding_amount": "$15M+",
                "deadline": "2024-11-15",
                "stage_appropriate": True,
                "requirements": "Market leader, expansion plans",
                "success_rate": "1%",
                "application_complexity": "Extremely High"
            }
        ]
    
    # Apply domain filter if specified
    if domain:
        opportunities = [opp for opp in opportunities if domain.lower() in opp["title"].lower()]
    
    # Apply country filter if specified
    if country:
        # This is simplified - in a real implementation, we'd have country data
        # Here we're just simulating country filtering
        opportunities = opportunities[:max(1, len(opportunities) - 1)]
    
    # Add guidance based on stage
    if current_stage == "Pre-seed":
        guidance = {
            "focus_areas": ["Clear problem statement", "Unique value proposition", "Early prototype"],
            "common_pitfalls": ["Lack of market validation", "Unrealistic funding expectations", "Over-engineering MVP"],
            "success_tips": ["Focus on problem-solution fit", "Build minimal viable product", "Network with angel investors"]
        }
    elif current_stage == "Seed":
        guidance = {
            "focus_areas": ["User traction metrics", "Clear business model", "Early revenue indicators"],
            "common_pitfalls": ["Scaling too early", "Ignoring unit economics", "Weak go-to-market strategy"],
            "success_tips": ["Demonstrate product-market fit", "Build key partnerships", "Show clear growth metrics"]
        }
    elif current_stage == "Series A":
        guidance = {
            "focus_areas": ["Revenue growth", "Scalable processes", "Market expansion plans"],
            "common_pitfalls": ["Unproven unit economics", "Weak management team", "Unclear differentiation"],
            "success_tips": ["Focus on consistent revenue", "Build strong team", "Clear path to profitability"]
        }
    else:  # Series B+
        guidance = {
            "focus_areas": ["Profitability path", "International expansion", "Industry leadership"],
            "common_pitfalls": ["Failure to adapt to market changes", "Overlooking competition", "Poor capital allocation"],
            "success_tips": ["Focus on sustainable growth", "Consider strategic partnerships", "Build for exit or IPO"]
        }
    
    return {
        "stage": current_stage,
        "opportunities": opportunities,
        "total_matched": len(opportunities),
        "guidance": guidance,
        "timestamp": datetime.now().isoformat()
    }


#
# Additional Integrated Endpoints
#

@router.get("/geographic-availability")
async def get_geographic_availability(db: AsyncSession = Depends(get_db)):
    """
    Get intelligence feed availability by geographic region
    This endpoint helps users understand which regions have available funding
    """
    # In a real implementation, this would query intelligence feed by geography
    # For now, we'll return a representative response
    
    geography_data = [
        {"region": "East Africa", "opportunity_count": 23, "total_funding": 5400000},
        {"region": "West Africa", "opportunity_count": 35, "total_funding": 8700000},
        {"region": "Southern Africa", "opportunity_count": 19, "total_funding": 6300000},
        {"region": "North Africa", "opportunity_count": 12, "total_funding": 3100000},
        {"region": "Central Africa", "opportunity_count": 7, "total_funding": 1500000}
    ]
    
    return {
        "geographic_availability": geography_data,
        "total_opportunities": sum(item["opportunity_count"] for item in geography_data),
        "total_funding": sum(item["total_funding"] for item in geography_data),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/domain-funding")
async def get_domain_funding(db: AsyncSession = Depends(get_db)):
    """
    Get intelligence feed by AI domain
    This endpoint helps users understand which AI domains receive the most funding
    """
    # In a real implementation, this would query intelligence feed by domain
    # For now, we'll return a representative response
    
    domain_data = [
        {"domain": "Healthcare", "opportunity_count": 18, "total_funding": 7200000},
        {"domain": "Agriculture", "opportunity_count": 15, "total_funding": 5800000},
        {"domain": "Education", "opportunity_count": 12, "total_funding": 3500000},
        {"domain": "Financial Services", "opportunity_count": 22, "total_funding": 8100000},
        {"domain": "Climate & Energy", "opportunity_count": 14, "total_funding": 4700000},
        {"domain": "Infrastructure", "opportunity_count": 8, "total_funding": 2900000},
        {"domain": "General AI", "opportunity_count": 7, "total_funding": 1800000}
    ]
    
    return {
        "domain_funding": domain_data,
        "total_opportunities": sum(item["opportunity_count"] for item in domain_data),
        "total_funding": sum(item["total_funding"] for item in domain_data),
        "timestamp": datetime.now().isoformat()
    }
