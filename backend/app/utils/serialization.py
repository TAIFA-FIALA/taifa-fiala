"""
TAIFA-FIALA API Serialization Utilities
Provides serialization helpers for the FastAPI backend
"""

import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, HttpUrl
from datetime import datetime, date
from decimal import Decimal


class TaifaJsonEncoder(json.JSONEncoder):
    """Custom JSON encoder for TAIFA-FIALA backend that handles:
    - Pydantic HttpUrl objects
    - DateTime objects
    - Decimal objects
    - Pydantic models
    """
    def default(self, obj: Any) -> Any:
        # Handle HttpUrl objects (common in our schemas)
        if obj.__class__.__name__ == "HttpUrl" or isinstance(obj, HttpUrl):
            return str(obj)
        
        # Handle datetime objects
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        # Handle Decimal objects (for currency values)
        if isinstance(obj, Decimal):
            return float(obj)
        
        # Handle Pydantic models
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        
        # Let the base class handle anything we don't know about
        return super().default(obj)


def serialize_json(data: Any) -> str:
    """Serialize data to JSON using our custom encoder"""
    return json.dumps(data, cls=TaifaJsonEncoder)


def prepare_for_json(data: Any) -> Any:
    """
    Recursively prepare a data structure for JSON serialization by converting:
    - HttpUrl to strings
    - datetime to ISO format strings
    - Decimal to float
    - Pydantic models to dictionaries
    
    This function handles nested dictionaries and lists
    """
    if isinstance(data, (str, int, float, bool)) or data is None:
        return data
    elif hasattr(data, "__class__") and data.__class__.__name__ == "HttpUrl":
        return str(data)
    elif isinstance(data, HttpUrl):
        return str(data)
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    elif isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, BaseModel):
        return prepare_for_json(data.model_dump())
    elif isinstance(data, dict):
        return {k: prepare_for_json(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [prepare_for_json(item) for item in data]
    else:
        # Try default JSON serialization, may raise TypeError
        try:
            json.dumps(data)
            return data
        except TypeError:
            # If it can't be serialized, convert to string
            return str(data)
