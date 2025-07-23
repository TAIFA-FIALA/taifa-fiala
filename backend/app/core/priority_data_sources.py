"""
Priority African Data Sources Configuration
==========================================

Configuration and management of high-priority African data sources
for intelligence item discovery, specifically targeting underserved
regions and priority sectors.

Based on architecture review recommendations focusing on:
- African Development Bank initiatives
- National AI strategy announcements  
- Regional Economic Communities
- Multi-language institutional sources
- Local innovation hubs
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Use relative import when running within the app package
try:
    from app.core.multilingual_search import SupportedLanguage
# Use absolute import when running from project root
except ImportError:
    from app.core.multilingual_search import SupportedLanguage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# PRIORITY SOURCE MODELS
# =============================================================================

class SourceCategory(Enum):
    """Categories of funding sources"""
    MULTILATERAL_BANK = "multilateral_bank"
    REGIONAL_BANK = "regional_bank"
    GOVERNMENT_AGENCY = "government_agency"
    RESEARCH_INSTITUTE = "research_institute"
    FOUNDATION = "foundation"
    INNOVATION_HUB = "innovation_hub"
    ACCELERATOR = "accelerator"
    VENTURE_FUND = "venture_fund"
    DEVELOPMENT_AGENCY = "development_agency"
    REGIONAL_ORGANIZATION = "regional_organization"

class GeographicScope(Enum):
    """Geographic scope of sources"""
    CONTINENTAL = "continental"
    REGIONAL = "regional"
    NATIONAL = "national"
    SUBREGIONAL = "subregional"

class SectorFocus(Enum):
    """Sector focus areas"""
    HEALTHCARE = "healthcare"
    AGRICULTURE = "agriculture"
    CLIMATE = "climate"
    EDUCATION = "education"
    FINTECH = "fintech"
    INFRASTRUCTURE = "infrastructure"
    GENERAL_TECH = "general_tech"
    MULTI_SECTOR = "multi_sector"

@dataclass
class DataSourceConfig:
    """Configuration for a priority data source"""
    source_id: str
    name: str
    category: SourceCategory
    geographic_scope: GeographicScope
    primary_language: SupportedLanguage
    secondary_languages: List[SupportedLanguage] = field(default_factory=list)
    
    # Source details
    base_url: str = ""
    rss_feeds: List[str] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    search_pages: List[str] = field(default_factory=list)
    
    # Focus areas
    sector_focus: List[SectorFocus] = field(default_factory=list)
    target_countries: List[str] = field(default_factory=list)
    
    # Equity metrics
    underserved_focus: bool = False
    women_focus: bool = False
    youth_focus: bool = False
    rural_focus: bool = False
    
    # Processing configuration
    search_frequency_hours: int = 24
    priority_weight: float = 1.0
    is_active: bool = True
    
    # Metadata
    description: str = ""
    contact_info: str = ""
    last_updated: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'source_id': self.source_id,
            'name': self.name,
            'category': self.category.value,
            'geographic_scope': self.geographic_scope.value,
            'primary_language': self.primary_language.value,
            'secondary_languages': [lang.value for lang in self.secondary_languages],
            'base_url': self.base_url,
            'rss_feeds': self.rss_feeds,
            'api_endpoints': self.api_endpoints,
            'search_pages': self.search_pages,
            'sector_focus': [sector.value for sector in self.sector_focus],
            'target_countries': self.target_countries,
            'underserved_focus': self.underserved_focus,
            'women_focus': self.women_focus,
            'youth_focus': self.youth_focus,
            'rural_focus': self.rural_focus,
            'search_frequency_hours': self.search_frequency_hours,
            'priority_weight': self.priority_weight,
            'is_active': self.is_active,
            'description': self.description,
            'contact_info': self.contact_info,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

# =============================================================================
# PRIORITY DATA SOURCES REGISTRY
# =============================================================================

class PriorityDataSourceRegistry:
    """Registry and management of priority African data sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sources = {}
        self._initialize_priority_sources()
    
    def _initialize_priority_sources(self):
        """Initialize the registry with priority African data sources"""
        
        # =============================================================================
        # MULTILATERAL DEVELOPMENT BANKS
        # =============================================================================
        
        # African Development Bank
        self.sources['afdb'] = DataSourceConfig(
            source_id='afdb',
            name='African Development Bank',
            category=SourceCategory.MULTILATERAL_BANK,
            geographic_scope=GeographicScope.CONTINENTAL,
            primary_language=SupportedLanguage.ENGLISH,
            secondary_languages=[SupportedLanguage.FRENCH, SupportedLanguage.ARABIC],
            base_url='https://www.afdb.org',
            rss_feeds=[
                'https://www.afdb.org/en/news-and-events/feed',
                'https://www.afdb.org/en/projects-operations/feed'
            ],
            search_pages=[
                'https://www.afdb.org/en/topics/digitalization',
                'https://www.afdb.org/en/topics/innovation',
                'https://www.afdb.org/en/funding'
            ],
            sector_focus=[SectorFocus.HEALTHCARE, SectorFocus.AGRICULTURE, SectorFocus.CLIMATE, SectorFocus.INFRASTRUCTURE],
            target_countries=['ALL_AFRICA'],
            underserved_focus=True,
            search_frequency_hours=12,
            priority_weight=2.0,
            description='Continental development bank with focus on infrastructure and innovation funding',
            contact_info='info@afdb.org'
        )
        
        # World Bank Africa
        self.sources['worldbank_africa'] = DataSourceConfig(
            source_id='worldbank_africa',
            name='World Bank Africa',
            category=SourceCategory.MULTILATERAL_BANK,
            geographic_scope=GeographicScope.CONTINENTAL,
            primary_language=SupportedLanguage.ENGLISH,
            secondary_languages=[SupportedLanguage.FRENCH, SupportedLanguage.ARABIC],
            base_url='https://www.worldbank.org/en/region/afr',
            rss_feeds=[
                'https://www.worldbank.org/en/region/afr/feed',
                'https://www.worldbank.org/en/topic/digitaldevelopment/feed'
            ],
            search_pages=[
                'https://www.worldbank.org/en/region/afr/funding',
                'https://www.worldbank.org/en/topic/digitaldevelopment'
            ],
            sector_focus=[SectorFocus.MULTI_SECTOR],
            target_countries=['ALL_AFRICA'],
            underserved_focus=True,
            priority_weight=1.8,
            description='World Bank Africa region funding and development programs'
        )
        
        # =============================================================================
        # REGIONAL DEVELOPMENT BANKS
        # =============================================================================
        
