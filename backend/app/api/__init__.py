from fastapi import APIRouter

from app.api.endpoints import (
    africa_intelligence_feed, organizations, domains, sources, analytics, search, rfp, source_validation,
    user_submissions, admin_scraping, automated_discovery, equity_analyses, stakeholder_reports
)
from app.api.v1.intelligent_search import router as intelligent_search_router

# Create main API router
api_router = APIRouter()

# Funding opportunities API endpoints
api_router.include_router(
    africa_intelligence_feed.router,
    prefix="/funding-opportunities",
    tags=["funding-opportunities"]
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

# New intelligent search with vector filtering (replaces deprecated RFPs)
api_router.include_router(
    intelligent_search_router,
    prefix="/v1/intelligent-search",
    tags=["intelligent-search"]
)

api_router.include_router(
    rfp.router, 
    prefix="/rfps", 
    tags=["rfps"]
)

api_router.include_router(
    source_validation.router, 
    prefix="/source-validation", 
    tags=["source-validation"]
)

# Include new 3-method data importation endpoints
api_router.include_router(
    user_submissions.router,
    prefix="/submissions",
    tags=["user-submissions"]
)

api_router.include_router(
    admin_scraping.router,
    prefix="/admin/scraping",
    tags=["admin-scraping"]
)

api_router.include_router(
    automated_discovery.router,
    prefix="/discovery",
    tags=["automated-discovery"]
)

# Opportunities endpoints now merged into funding-opportunities

api_router.include_router(
    equity_analyses.router,
    prefix="/equity-analyses",
    tags=["equity-analyses"]
)

# Stakeholder reports for executive insights
api_router.include_router(
    stakeholder_reports.router,
    prefix="/reports",
    tags=["stakeholder-reports"]
)
