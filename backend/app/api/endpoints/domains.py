from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_domains():
    """Get AI domains and categories"""
    return {"message": "AI domains endpoint - coming soon"}

@router.get("/categories")
async def get_funding_categories():
    """Get funding categories"""
    return {"message": "Funding categories endpoint - coming soon"}
