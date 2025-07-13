from fastapi import APIRouter

from app.api.endpoints import (
    funding, organizations, domains, sources, analytics, search, rfp, source_validation,
    user_submissions, admin_scraping, automated_discovery
)

# Create main API router
api_router = APIRouter()

# Include existing endpoint routers
api_router.include_router(
    funding.router, 
    prefix="/funding-opportunities", 
    tags=["funding"]
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
