from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_data_sources():
    """Get data sources"""
    return {"message": "Data sources endpoint - coming soon"}

@router.get("/{source_id}/status")
async def get_source_status(source_id: int):
    """Get data source status"""
    return {"message": f"Data source {source_id} status - coming soon"}
