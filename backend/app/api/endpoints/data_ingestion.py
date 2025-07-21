from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.services.data_ingestion.master_pipeline import MasterDataIngestionPipeline, create_default_config
from app.core.config import settings
import logging
import traceback
import os
from pathlib import Path

# Ensure logs directory exists
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True, parents=True)
log_file = log_dir / "data_ingestion.log"

# Clear any existing handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Set up logging with absolute path
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Log the log file location
logger.info(f"Logging to {log_file.absolute()}")

router = APIRouter()

@router.post("/trigger")
async def trigger_data_ingestion():
    """
    Manually trigger the master data ingestion pipeline.
    Returns detailed status and logs of the ingestion process.
    """
    try:
        logger.info("=" * 50)
        logger.info("STARTING DATA INGESTION PIPELINE")
        logger.info("=" * 50)
        
        # Create default configuration
        logger.info("Creating pipeline configuration...")
        pipeline_config = create_default_config()
        
        if not pipeline_config:
            error_msg = "Failed to create pipeline configuration"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info("Pipeline config created successfully")
        
        # Initialize pipeline with both config and settings
        logger.info("Initializing pipeline...")
        pipeline = MasterDataIngestionPipeline(config=pipeline_config, settings=settings)
        
        if not hasattr(pipeline, 'start'):
            error_msg = "Pipeline instance has no method 'start'"
            logger.error(error_msg)
            raise AttributeError(error_msg)
            
        logger.info("Pipeline initialized, starting ingestion...")
        
        # Start the ingestion process
        result = await pipeline.start()
        
        logger.info("=" * 50)
        logger.info("DATA INGESTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
        
        return JSONResponse(content={
            "status": "success",
            "message": "Data ingestion pipeline completed successfully",
            "log_file": str(log_file.absolute())
        })
        
    except Exception as e:
        error_trace = traceback.format_exc()
        error_msg = f"Error in data ingestion: {str(e)}\n{error_trace}"
        logger.error(error_msg)
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "log_file": str(log_file.absolute()),
                "details": f"Check the log file for full error details: {log_file.absolute()}"
            }
        )