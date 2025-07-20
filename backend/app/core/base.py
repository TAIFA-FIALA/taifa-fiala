"""
SQLAlchemy Base Configuration

This module defines the SQLAlchemy Base class that should be used by all models.
It helps avoid circular imports by centralizing the Base definition.
"""
from sqlalchemy.ext.declarative import declarative_base

# Create a declarative base class for all models
Base = declarative_base()

# This allows us to import Base in models without causing circular imports
