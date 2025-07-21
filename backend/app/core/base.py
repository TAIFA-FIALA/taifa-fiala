"""
SQLAlchemy Base Configuration

This module defines the SQLAlchemy Base class that should be used by all models.
It helps avoid circular imports by centralizing the Base definition.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# Define a naming convention for constraints to support automatic naming
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create a custom metadata instance with the naming convention
metadata = MetaData(naming_convention=convention)

# Create a declarative base class for all models
Base = declarative_base(metadata=metadata)

# This allows us to import Base in models without causing circular imports
