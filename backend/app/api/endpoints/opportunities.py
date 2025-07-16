from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import FundingOpportunity, Organization, AIDomain, FundingType

router = APIRouter()

@router.get("/stage-matching")
async def get_stage_matched_opportunities(
    stage: str = Query(None, description="Funding stage to match (e.g., 'Pre-seed', 'Seed', 'Series A')"),
    domain: str = Query(None, description="AI domain to filter by"),
    country: str = Query(None, description="Country to filter by"),
    db: Session = Depends(get_db)
):
    """
    Get funding opportunities matched to a specific stage and optionally filtered by domain and country.
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
                "deadline": "2024-07-30",
                "stage_appropriate": True,
                "requirements": "MVP and team formation",
                "success_rate": "12%",
                "application_complexity": "Medium"
            },
            {
                "id": 103,
                "title": "UNICEF Innovation Fund",
                "organization": "UNICEF",
                "funding_amount": "Up to $30,000",
                "deadline": "2024-09-10",
                "stage_appropriate": True,
                "requirements": "Open source technology, early prototype",
                "success_rate": "8%",
                "application_complexity": "Medium"
            }
        ]
    elif current_stage == "Seed":
        opportunities = [
            {
                "id": 201,
                "title": "Africa AI Accelerator",
                "organization": "Microsoft4Africa",
                "funding_amount": "Up to $150,000",
                "deadline": "2024-08-30",
                "stage_appropriate": True,
                "requirements": "Working product, early traction",
                "success_rate": "10%",
                "application_complexity": "Medium"
            },
            {
                "id": 202,
                "title": "Norrsken Impact Accelerator",
                "organization": "Norrsken Foundation",
                "funding_amount": "Up to $100,000",
                "deadline": "2024-07-15",
                "stage_appropriate": True,
                "requirements": "Revenue generating, impact metrics",
                "success_rate": "7%",
                "application_complexity": "High"
            },
            {
                "id": 203,
                "title": "Founders Factory Africa",
                "organization": "Founders Factory",
                "funding_amount": "Up to $120,000",
                "deadline": "2024-09-05",
                "stage_appropriate": True,
                "requirements": "Market validation, scalable solution",
                "success_rate": "6%",
                "application_complexity": "High"
            }
        ]
    elif current_stage == "Series A":
        opportunities = [
            {
                "id": 301,
                "title": "Partech Africa Fund",
                "organization": "Partech Partners",
                "funding_amount": "$1-3 million",
                "deadline": "Rolling applications",
                "stage_appropriate": True,
                "requirements": "Significant traction, scaling operations",
                "success_rate": "4%",
                "application_complexity": "Very high"
            },
            {
                "id": 302,
                "title": "TLcom TIDE Africa Fund",
                "organization": "TLcom Capital",
                "funding_amount": "$1-5 million",
                "deadline": "Rolling applications",
                "stage_appropriate": True,
                "requirements": "Revenue growth, expanding market",
                "success_rate": "3%",
                "application_complexity": "Very high"
            }
        ]
    else:  # Series B and beyond
        opportunities = [
            {
                "id": 401,
                "title": "Novastar Ventures",
                "organization": "Novastar",
                "funding_amount": "$5-15 million",
                "deadline": "Rolling applications",
                "stage_appropriate": True,
                "requirements": "Proven business model, expansion ready",
                "success_rate": "2%",
                "application_complexity": "Extremely high"
            },
            {
                "id": 402,
                "title": "Africa Transformation Fund",
                "organization": "AfricInvest",
                "funding_amount": "$10-30 million",
                "deadline": "Rolling applications",
                "stage_appropriate": True,
                "requirements": "Market leadership, strong financials",
                "success_rate": "1%",
                "application_complexity": "Extremely high"
            }
        ]
    
    # Filter by domain if provided
    if domain:
        # In a real implementation, this would filter based on actual domain data
        # For demo, we'll just simulate filtering
        opportunities = opportunities[:2]  # Just return fewer items to simulate filtering
    
    # Filter by country if provided
    if country:
        # In a real implementation, this would filter based on country eligibility
        # For demo, we'll just simulate filtering
        opportunities = opportunities[:2]  # Just return fewer items to simulate filtering
    
    # Next steps guidance based on stage
    next_steps = {
        "Pre-seed": "Focus on building an MVP, validating problem-solution fit, and forming a strong team.",
        "Seed": "Demonstrate product-market fit, acquire early customers, and build scalable processes.",
        "Series A": "Focus on scaling operations, entering new markets, and optimizing your unit economics.",
        "Series B": "Expand internationally, develop new product lines, and prepare for potential exits.",
        "Series C+": "Consider M&A opportunities, prepare for IPO, or focus on profitability and market leadership."
    }
    
    # Common pitfalls to avoid
    pitfalls = {
        "Pre-seed": [
            "Seeking too much funding before validation",
            "Over-engineering product features",
            "Neglecting user research"
        ],
        "Seed": [
            "Expanding too quickly before product-market fit",
            "Underestimating customer acquisition costs",
            "Poor financial modeling"
        ],
        "Series A": [
            "Premature scaling without infrastructure",
            "Neglecting unit economics",
            "Failing to develop middle management"
        ],
        "Series B": [
            "Losing focus on core business",
            "International expansion without localization",
            "Neglecting company culture during rapid growth"
        ],
        "Series C+": [
            "Becoming too rigid in operations",
            "Failing to innovate beyond core products",
            "Ignoring competition from agile startups"
        ]
    }
    
    return {
        "stage": current_stage,
        "opportunities": opportunities,
        "total_opportunities": len(opportunities),
        "next_steps_guidance": next_steps.get(current_stage, ""),
        "common_pitfalls": pitfalls.get(current_stage, []),
        "timestamp": datetime.now().isoformat()
    }
