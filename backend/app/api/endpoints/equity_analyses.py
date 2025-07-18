from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, desc, cast, Float
from datetime import datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.models import Organization, AfricaIntelligenceItem, CommunityUser, GeographicScope, AIDomain

router = APIRouter()

@router.get("/summary")
async def get_equity_summary(db: Session = Depends(get_db)):
    """Get a summary of key equity metrics for the dashboard"""
    
    # Get total funding opportunities
    total_opportunities = db.query(func.count(distinct(AfricaIntelligenceItem.id))).scalar() or 0
    
    # Get total funding amount
    total_funding = db.query(func.sum(cast(AfricaIntelligenceItem.funding_amount, Float))).scalar() or 0
    
    # Get geographic distribution summary (top 5)
    geo_distribution = db.query(
        GeographicScope.name,
        func.count(distinct(AfricaIntelligenceItem.id)).label('opportunity_count')
    ).join(
        AfricaIntelligenceItem.geographic_scopes
    ).filter(
        GeographicScope.scope_type == 'country'
    ).group_by(
        GeographicScope.name
    ).order_by(
        desc('opportunity_count')
    ).limit(5).all()
    
    # Get domain distribution summary (top 5)
    domain_distribution = db.query(
        AIDomain.name,
        func.count(distinct(AfricaIntelligenceItem.id)).label('opportunity_count')
    ).join(
        AfricaIntelligenceItem.domains
    ).group_by(
        AIDomain.name
    ).order_by(
        desc('opportunity_count')
    ).limit(5).all()
    
    # Get organization type distribution
    org_distribution = db.query(
        Organization.recipient_type,
        func.count(distinct(Organization.id)).label('org_count')
    ).filter(
        Organization.recipient_type.isnot(None)
    ).group_by(
        Organization.recipient_type
    ).all()
    
    return {
        "total_opportunities": total_opportunities,
        "total_funding": float(total_funding),
        "geographic_distribution": [
            {"name": geo[0], "count": geo[1]} for geo in geo_distribution
        ],
        "domain_distribution": [
            {"name": domain[0], "count": domain[1]} for domain in domain_distribution
        ],
        "organization_distribution": [
            {"type": org[0], "count": org[1]} for org in org_distribution
        ]
    }

@router.get("/geographical")
async def get_geographical_distribution(db: Session = Depends(get_db)):
    """Get geographical funding distribution"""
    # Query to get funding by region/country
    results = db.query(
        GeographicScope.name,
        GeographicScope.scope_type,
        func.count(distinct(AfricaIntelligenceItem.id)).label('opportunity_count'),
        func.sum(cast(AfricaIntelligenceItem.funding_amount, Float)).label('total_funding')
    ).join(
        AfricaIntelligenceItem.geographic_scopes
    ).filter(
        GeographicScope.scope_type.in_(['country', 'region']),
        GeographicScope.name.in_([
            'Nigeria', 'Kenya', 'South Africa', 'Egypt', 'Ghana',
            'Rwanda', 'Ethiopia', 'Uganda', 'Senegal', 'Tanzania',
            'Morocco', 'Tunisia', 'Cameroon', 'Mali', 'Chad'
        ])
    ).group_by(
        GeographicScope.name, GeographicScope.scope_type
    ).all()
    
    # Calculate total funding for percentage calculations
    total_funding = sum(row[3] for row in results) if results else 0
    
    # Format results
    distribution = [{
        "country_name": row[0],
        "country_code": row[0][:2].upper(),  # Simple way to get country code
        "opportunity_count": row[2],
        "total_funding": float(row[3]) if row[3] else 0.0,
        "percentage_of_total": (float(row[3]) / total_funding * 100) if total_funding > 0 else 0.0
    } for row in results]
    
    # Calculate Gini coefficient (measure of funding inequality)
    gini = calculate_gini_coefficient([item["total_funding"] for item in distribution]) if distribution else 0
    
    return {
        "distribution": distribution,
        "total_funding": total_funding,
        "gini_coefficient": gini,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/gender-distribution")
async def get_gender_distribution(db: Session = Depends(get_db)):
    """Get gender distribution of funding recipients"""
    # This would normally query from a users or founders table with gender information
    # For demo purposes, we'll return representative data for Africa
    
    # Mock data based on the fact that female founders receive only 2% of funding
    gender_data = [
        {"gender": "Male", "funding_percentage": 98.0, "opportunity_count": 245, "total_funding": 9800000},
        {"gender": "Female", "funding_percentage": 2.0, "opportunity_count": 5, "total_funding": 200000},
    ]
    
    # Historical trend data (showing slow improvement)
    historical_data = [
        {"year": 2020, "male_percentage": 99.0, "female_percentage": 1.0},
        {"year": 2021, "male_percentage": 98.5, "female_percentage": 1.5},
        {"year": 2022, "male_percentage": 98.0, "female_percentage": 2.0},
        {"year": 2023, "male_percentage": 97.5, "female_percentage": 2.5},
        {"year": 2024, "male_percentage": 96.8, "female_percentage": 3.2},
        {"year": 2025, "male_percentage": 96.0, "female_percentage": 4.0},
    ]
    
    return {
        "current_distribution": gender_data,
        "historical_trend": historical_data,
        "total_funding": sum(item["total_funding"] for item in gender_data),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/inclusion-trends")
async def get_inclusion_trends(db: Session = Depends(get_db)):
    """Get trends in funding inclusion across different dimensions"""
    # In a real implementation, this would query actual demographic data
    # For demo purposes, we'll return representative data
    
    # Regional inclusion data
    regional_data = [
        {"region": "East Africa", "funding_percentage": 28.5, "change_from_previous_year": 2.1},
        {"region": "West Africa", "funding_percentage": 35.7, "change_from_previous_year": 3.5},
        {"region": "Southern Africa", "funding_percentage": 24.2, "change_from_previous_year": -1.8},
        {"region": "North Africa", "funding_percentage": 10.5, "change_from_previous_year": 0.7},
        {"region": "Central Africa", "funding_percentage": 1.1, "change_from_previous_year": 0.2}
    ]
    
    # Language diversity data
    language_data = [
        {"language": "English", "percentage_of_opportunities": 76.3},
        {"language": "French", "percentage_of_opportunities": 15.7},
        {"language": "Arabic", "percentage_of_opportunities": 5.2},
        {"language": "Portuguese", "percentage_of_opportunities": 2.5},
        {"language": "Swahili", "percentage_of_opportunities": 0.3}
    ]
    
    # Underrepresented groups data
    underrepresented_data = [
        {"group": "Youth-led initiatives", "funding_percentage": 12.3, "change_from_previous_year": 4.2},
        {"group": "Women-led initiatives", "funding_percentage": 2.0, "change_from_previous_year": 0.5},
        {"group": "Rural communities", "funding_percentage": 8.1, "change_from_previous_year": 1.3},
        {"group": "Disabled entrepreneurs", "funding_percentage": 0.8, "change_from_previous_year": 0.3}
    ]
    
    return {
        "regional_inclusion": regional_data,
        "language_diversity": language_data,
        "underrepresented_groups": underrepresented_data,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/featured-founders")
async def get_featured_founders(db: Session = Depends(get_db)):
    """Get featured founders with focus on underrepresented groups"""
    # This would normally query from a founders or success stories database
    # For demo purposes, we'll return representative data
    
    featured_founders = [
        {
            "name": "Amara Okonkwo",
            "country": "Nigeria",
            "organization": "HealthAI Africa",
            "funding_secured": 750000,
            "ai_domain": "Healthcare",
            "story": "Founded HealthAI Africa to develop diagnostic tools for rural communities using machine learning. Secured funding after 18 rejected applications.",
            "image_url": "https://randomuser.me/api/portraits/women/65.jpg",
            "underrepresented_group": "Women in AI"
        },
        {
            "name": "Kwame Mensah",
            "country": "Ghana",
            "organization": "AgroPredict",
            "funding_secured": 420000,
            "ai_domain": "Agriculture",
            "story": "Developed AI systems to help smallholder farmers predict optimal planting times and crop selection based on climate data.",
            "image_url": "https://randomuser.me/api/portraits/men/32.jpg",
            "underrepresented_group": "Rural innovation"
        },
        {
            "name": "Nala Diop",
            "country": "Senegal",
            "organization": "EdTech Futures",
            "funding_secured": 380000,
            "ai_domain": "Education",
            "story": "Created adaptive learning platforms that work in low-connectivity environments to improve education access in rural Senegal.",
            "image_url": "https://randomuser.me/api/portraits/women/22.jpg",
            "underrepresented_group": "Francophone founders"
        },
        {
            "name": "Tendai Moyo",
            "country": "Zimbabwe",
            "organization": "RenewAI",
            "funding_secured": 290000,
            "ai_domain": "Climate",
            "story": "Built AI systems for optimizing renewable energy deployment in off-grid communities across Southern Africa.",
            "image_url": "https://randomuser.me/api/portraits/women/45.jpg",
            "underrepresented_group": "Climate tech"
        }
    ]
    
    return {
        "featured_founders": featured_founders,
        "total_featured": len(featured_founders),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/funding-stages")
async def get_funding_stages(db: Session = Depends(get_db)):
    """Get funding stage distribution and progression data"""
    # This would normally query from intelligence feed with stage information
    # For demo purposes, we'll return representative data based on the statistic
    # that 69% of deals are stuck at seed stage
    
    # Current stage distribution
    stage_distribution = [
        {"stage": "Pre-seed", "percentage": 12.5, "opportunity_count": 25, "avg_funding": 25000},
        {"stage": "Seed", "percentage": 69.0, "opportunity_count": 138, "avg_funding": 150000},
        {"stage": "Series A", "percentage": 14.2, "opportunity_count": 28, "avg_funding": 1200000},
        {"stage": "Series B", "percentage": 3.3, "opportunity_count": 7, "avg_funding": 5000000},
        {"stage": "Series C+", "percentage": 1.0, "opportunity_count": 2, "avg_funding": 15000000}
    ]
    
    # Stage progression data (percentage of companies advancing from one stage to the next)
    stage_progression = [
        {"from_stage": "Pre-seed", "to_stage": "Seed", "progression_rate": 72.0},
        {"from_stage": "Seed", "to_stage": "Series A", "progression_rate": 18.5},
        {"from_stage": "Series A", "to_stage": "Series B", "progression_rate": 22.0},
        {"from_stage": "Series B", "to_stage": "Series C+", "progression_rate": 15.0}
    ]
    
    # Time spent at each stage (months)
    time_in_stage = [
        {"stage": "Pre-seed", "avg_months": 12},
        {"stage": "Seed", "avg_months": 24},
        {"stage": "Series A", "avg_months": 18},
        {"stage": "Series B", "avg_months": 15},
        {"stage": "Series C+", "avg_months": 12}
    ]
    
    return {
        "stage_distribution": stage_distribution,
        "stage_progression": stage_progression,
        "time_in_stage": time_in_stage,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/funding-distribution")
async def get_funding_distribution(db: Session = Depends(get_db)):
    """Get detailed funding distribution across African countries"""
    # This would normally query from intelligence feed with geographic data
    # For demo purposes, we'll return representative data based on the 83% statistic
    
    # Mock data showing 83% of funding goes to top 4 countries
    countries = [
        {"country_name": "Nigeria", "country_code": "NG", "total_funding": 4500000, "opportunity_count": 32, "percentage_of_total": 45.0},
        {"country_name": "Kenya", "country_code": "KE", "total_funding": 1800000, "opportunity_count": 22, "percentage_of_total": 18.0},
        {"country_name": "South Africa", "country_code": "ZA", "total_funding": 1200000, "opportunity_count": 18, "percentage_of_total": 12.0},
        {"country_name": "Egypt", "country_code": "EG", "total_funding": 800000, "opportunity_count": 12, "percentage_of_total": 8.0},
        {"country_name": "Ghana", "country_code": "GH", "total_funding": 350000, "opportunity_count": 6, "percentage_of_total": 3.5},
        {"country_name": "Rwanda", "country_code": "RW", "total_funding": 320000, "opportunity_count": 5, "percentage_of_total": 3.2},
        {"country_name": "Ethiopia", "country_code": "ET", "total_funding": 310000, "opportunity_count": 4, "percentage_of_total": 3.1},
        {"country_name": "Uganda", "country_code": "UG", "total_funding": 290000, "opportunity_count": 4, "percentage_of_total": 2.9},
        {"country_name": "Senegal", "country_code": "SN", "total_funding": 180000, "opportunity_count": 3, "percentage_of_total": 1.8},
        {"country_name": "Tanzania", "country_code": "TZ", "total_funding": 120000, "opportunity_count": 2, "percentage_of_total": 1.2},
        {"country_name": "Morocco", "country_code": "MA", "total_funding": 80000, "opportunity_count": 2, "percentage_of_total": 0.8},
        {"country_name": "Tunisia", "country_code": "TN", "total_funding": 25000, "opportunity_count": 1, "percentage_of_total": 0.25},
        {"country_name": "Cameroon", "country_code": "CM", "total_funding": 15000, "opportunity_count": 1, "percentage_of_total": 0.15},
        {"country_name": "Mali", "country_code": "ML", "total_funding": 5000, "opportunity_count": 1, "percentage_of_total": 0.05},
        {"country_name": "Chad", "country_code": "TD", "total_funding": 5000, "opportunity_count": 1, "percentage_of_total": 0.05}
    ]
    
    # Calculate statistics
    total_funding = sum(country["total_funding"] for country in countries)
    top_4_funding = sum(country["total_funding"] for country in countries[:4])
    top_4_percentage = (top_4_funding / total_funding) * 100 if total_funding > 0 else 0
    underserved_count = sum(1 for country in countries if country["percentage_of_total"] < 2.0)
    
    # Calculate Gini coefficient (measure of funding inequality)
    gini = calculate_gini_coefficient([country["total_funding"] for country in countries])
    
    return {
        "countries": countries,
        "total_funding": total_funding,
        "top_4_countries_percentage": top_4_percentage,
        "underserved_countries_count": underserved_count,
        "gini_coefficient": gini,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/collaboration-suggestions")
async def get_collaboration_suggestions(db: Session = Depends(get_db)):
    """Get collaboration suggestions for organizations and projects"""
    # In a real implementation, this would use an algorithm to match organizations based on
    # complementary strengths, shared interests, or geographic proximity
    # For demo purposes, we'll return representative suggestions
    
    collaboration_suggestions = [
        {
            "organization1": {
                "name": "AfriTech Innovation Hub",
                "country": "Kenya",
                "strength": "Technical infrastructure",
                "funding_stage": "Series A"
            },
            "organization2": {
                "name": "MediAI Solutions",
                "country": "Rwanda",
                "strength": "Healthcare expertise",
                "funding_stage": "Seed"
            },
            "collaboration_potential": 87,
            "rationale": "Complementary technical and domain expertise for healthcare AI applications",
            "suggested_opportunities": ["WHO Global Health Innovation Grant", "Gates Foundation Healthcare AI Challenge"]
        },
        {
            "organization1": {
                "name": "Data Science Nigeria",
                "country": "Nigeria",
                "strength": "Data science talent",
                "funding_stage": "Series B"
            },
            "organization2": {
                "name": "AgriTech Ghana",
                "country": "Ghana",
                "strength": "Agricultural domain knowledge",
                "funding_stage": "Seed"
            },
            "collaboration_potential": 92,
            "rationale": "Combined data science expertise with agricultural knowledge for farming optimization",
            "suggested_opportunities": ["USAID Innovation Fund", "African Development Bank AgriTech Grant"]
        },
        {
            "organization1": {
                "name": "SolarAI Ventures",
                "country": "Morocco",
                "strength": "Renewable energy technology",
                "funding_stage": "Seed"
            },
            "organization2": {
                "name": "Sahel Climate Tech",
                "country": "Mali",
                "strength": "Regional deployment experience",
                "funding_stage": "Pre-seed"
            },
            "collaboration_potential": 85,
            "rationale": "Technology and deployment synergy for renewable energy in Sahel region",
            "suggested_opportunities": ["Green Climate Fund", "African Renewable Energy Initiative"]
        },
        {
            "organization1": {
                "name": "EduTech Tanzania",
                "country": "Tanzania",
                "strength": "Educational content",
                "funding_stage": "Seed"
            },
            "organization2": {
                "name": "Connectivity Solutions Ethiopia",
                "country": "Ethiopia",
                "strength": "Rural internet infrastructure",
                "funding_stage": "Seed"
            },
            "collaboration_potential": 79,
            "rationale": "Combining educational content with connectivity solutions for rural education",
            "suggested_opportunities": ["UNESCO Digital Learning Fund", "Mastercard Foundation EdTech Challenge"]
        }
    ]
    
    return {
        "collaboration_suggestions": collaboration_suggestions,
        "total_suggestions": len(collaboration_suggestions),
        "timestamp": datetime.now().isoformat()
    }


def calculate_gini_coefficient(values):
    """Calculate Gini coefficient as a measure of inequality"""
    # Ensure values is not empty
    if not values or sum(values) == 0:
        return 0
        
    # Sort values in ascending order
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    # Calculate Gini coefficient
    cumulative_values = [sum(sorted_values[:i+1]) for i in range(n)]
    total = cumulative_values[-1]
    
    # Compute Gini using the area under the Lorenz curve
    area_under_lorenz = sum(cumulative_values) / (n * total) if total > 0 else 0
    gini = 1 - (2 * area_under_lorenz - (1/n))
    
    return round(gini, 3)
