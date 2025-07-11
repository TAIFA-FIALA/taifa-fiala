from fastapi import APIRouter

from app.api.endpoints import funding, organizations, domains, sources, analytics, search, rfp

# Create main API router
api_router = APIRouter()

# Include endpoint routers
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
