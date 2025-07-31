from fastapi import APIRouter

# Minimal working imports to get backend running
from .endpoints import (
    africa_intelligence_feed,
    organizations,
    domains,
    sources,
    analytics,
    search,
    funding_opportunities,
    equity_analyses,
    events
)
# Events router already imported above
from app.core.database import get_db 

# Create main API router
api_router = APIRouter()

# Include ETL monitoring endpoints without adding an additional prefix
# The router already has the full path prefix included
# api_router.include_router(
#     etl_monitoring.router,
#     prefix="",  # No additional prefix
#     tags=["etl-monitoring"]
# )

# Core working endpoints only
api_router.include_router(
    africa_intelligence_feed.router,
    prefix="/funding-opportunities",
    tags=["funding-opportunities"]
)

api_router.include_router(
    funding_opportunities.router,
    prefix="/funding-opportunities",
    tags=["funding-opportunities-v2"]
)

api_router.include_router(
    organizations.router, 
    prefix="/organizations", 
    tags=["organizations"]
)

api_router.include_router(
    domains.router, 
    prefix="/domains", 
    tags=["domains"]
)

api_router.include_router(
    sources.router, 
    prefix="/data-sources", 
    tags=["data-sources"]
)

api_router.include_router(
    analytics.router, 
    prefix="/analytics", 
    tags=["analytics"]
)

api_router.include_router(
    search.router, 
    prefix="/search", 
    tags=["search"]
)

api_router.include_router(
    equity_analyses.router,
    prefix="/equity-analyses",
    tags=["equity-analyses"]
)

# New intelligent search with vector filtering (replaces deprecated RFPs)
# api_router.include_router(
#     intelligent_search.router,
#     tags=["intelligent-search"]
# )

# api_router.include_router(
#     rfp.router, 
#     prefix="/rfps", 
#     tags=["rfps"]
# )

# api_router.include_router(
#     source_validation.router, 
#     prefix="/source-validation", 
#     tags=["source-validation"]
# )

# Include new 3-method data importation endpoints
# api_router.include_router(
#     user_submissions.router,
#     prefix="/submissions",
#     tags=["user-submissions"]
# )

# api_router.include_router(
#     admin_scraping.router,
#     prefix="/admin/scraping",
#     tags=["admin-scraping"]
# )

# api_router.include_router(
#     data_ingestion.router,
#     prefix="/data-ingestion",
#     tags=["data-ingestion"]
# )

# api_router.include_router(
#     automated_discovery.router,
#     prefix="/discovery",
#     tags=["automated-discovery"]
# )

# Opportunities endpoints now merged into funding-opportunities

api_router.include_router(
    equity_analyses.router,
    prefix="/equity-analyses",
    tags=["equity-analyses"]
)

# Stakeholder reports for executive insights
# api_router.include_router(
#     stakeholder_reports.router,
#     prefix="/reports",
#     tags=["stakeholder-reports"]
# )

# Enhanced notification system for monitoring alerts
# api_router.include_router(
#     notifications.router,
#     tags=["notifications"]
# )

# Account balance monitoring for LLM providers
# api_router.include_router(
#     balance_monitoring.router,
#     tags=["balance-monitoring"]
# )

# Server-Sent Events for real-time updates
api_router.include_router(
    events.router,
    prefix="/events",
    tags=["events"]
)
