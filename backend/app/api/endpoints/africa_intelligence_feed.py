"""
Africa Intelligence Feed Compatibility Module
=============================================

This module provides backward compatibility for the refactored API structure.
It re-exports the router from funding_opportunities.py to maintain
compatibility with existing imports.
"""

# Handle multiple import paths for compatibility
try:
    # Try relative import first (within the same package)
    from .funding_opportunities import router
except ImportError:
    try:
        # Try absolute import with app prefix
        from app.api.endpoints.funding_opportunities import router
    except ImportError:
        # Try absolute import with backend prefix
        from app.api.endpoints.funding_opportunities import router

# This maintains backward compatibility while using the unified implementation
