from typing import Dict
import logging

# Use relative import when running within the app package
try:
    from app.core.priority_data_sources import (
        DataSourceConfig, SourceCategory, GeographicScope,
        SupportedLanguage, SectorFocus
    )
# Use absolute import when running from project root
except ImportError:
    from app.core.priority_data_sources import (
        DataSourceConfig, SourceCategory, GeographicScope,
        SupportedLanguage, SectorFocus
    )


class PriorityDataSourceRegistry:
    """Registry for managing and prioritizing data sources for funding opportunities"""
    
    def __init__(self):
        """Initialize the priority data sources registry"""
        self.sources: Dict[str, DataSourceConfig] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Initialize the default set of data sources"""
        
        # =============================================================================
        # REGIONAL DEVELOPMENT BANKS
        # =============================================================================
        
        # West African Development Bank (BOAD)
        self.sources['boad'] = DataSourceConfig(
            source_id='boad',
            name='West African Development Bank (BOAD)',
            category=SourceCategory.REGIONAL_BANK,
            geographic_scope=GeographicScope.REGIONAL,
            primary_language=SupportedLanguage.FRENCH,
            secondary_languages=[SupportedLanguage.ENGLISH],
            base_url='https://www.boad.org',
            rss_feeds=['https://www.boad.org/feed'],
            search_pages=[
                'https://www.boad.org/financement',
                'https://www.boad.org/appels-offres'
            ],
            sector_focus=[SectorFocus.AGRICULTURE, SectorFocus.INFRASTRUCTURE, SectorFocus.HEALTHCARE],
            target_countries=['BJ', 'BF', 'CI', 'GW', 'ML', 'NE', 'SN', 'TG'],
            underserved_focus=True,
            rural_focus=True,
            search_frequency_hours=24,
            priority_weight=1.5,
            description='Regional development bank for West Africa with focus on rural development'
        )

        # Development Bank of Central African States (BDEAC)
        self.sources['bdeac'] = DataSourceConfig(
            source_id='bdeac',
            name='Development Bank of Central African States (BDEAC)',
            category=SourceCategory.REGIONAL_BANK,
            geographic_scope=GeographicScope.REGIONAL,
            primary_language=SupportedLanguage.FRENCH,
            secondary_languages=[SupportedLanguage.ENGLISH],
            base_url='https://www.bdeac.org',
            search_pages=[
                'https://www.bdeac.org/financement',
                'https://www.bdeac.org/projets'
            ],
            sector_focus=[SectorFocus.AGRICULTURE, SectorFocus.INFRASTRUCTURE, SectorFocus.CLIMATE],
            target_countries=['CM', 'CF', 'TD', 'CG', 'GQ', 'GA'],
            underserved_focus=True,
            rural_focus=True,
            search_frequency_hours=24,
            priority_weight=2.0,  # Higher priority for underserved Central Africa
            description='Regional development bank for Central Africa, critical for underserved regions'
        )
        # =============================================================================
        # DEVELOPMENT AGENCIES
        # =============================================================================

        # Agence Française de Développement (AFD)
        self.sources['afd'] = DataSourceConfig(
            source_id='afd',
            name='Agence Française de Développement (AFD)',
            category=SourceCategory.DEVELOPMENT_AGENCY,
            geographic_scope=GeographicScope.CONTINENTAL,
            primary_language=SupportedLanguage.FRENCH,
            secondary_languages=[SupportedLanguage.ENGLISH],
            base_url='https://www.afd.fr',
            rss_feeds=[
                'https://www.afd.fr/fr/actualites/feed',
                'https://www.afd.fr/fr/appels-candidatures/feed'
            ],
            search_pages=[
                'https://www.afd.fr/fr/appels-candidatures',
                'https://www.afd.fr/fr/page-region-pays/afrique'
            ],
            sector_focus=[SectorFocus.HEALTHCARE, SectorFocus.AGRICULTURE, SectorFocus.CLIMATE, SectorFocus.EDUCATION],
            target_countries=['ALL_FRANCOPHONE_AFRICA'],
            underserved_focus=True,
            women_focus=True,
            youth_focus=True,
            search_frequency_hours=12,
            priority_weight=1.8,
            description='French development agency with strong focus on francophone Africa'
        )
        
        # USAID Africa
        self.sources['usaid_africa'] = DataSourceConfig(
            source_id='usaid_africa',
            name='USAID Africa',
            category=SourceCategory.DEVELOPMENT_AGENCY,
            geographic_scope=GeographicScope.CONTINENTAL,
            primary_language=SupportedLanguage.ENGLISH,
            base_url='https://www.usaid.gov/africa',
            rss_feeds=['https://www.usaid.gov/africa/feed'],
            search_pages=[
                'https://www.usaid.gov/africa/funding-opportunities',
                'https://www.usaid.gov/digital-development'
            ],
            sector_focus=[SectorFocus.HEALTHCARE, SectorFocus.AGRICULTURE, SectorFocus.EDUCATION],
            target_countries=['ALL_AFRICA'],
            underserved_focus=True,
            women_focus=True,
            priority_weight=1.5,
            description='US development agency with significant African programs'
        )
        
        # =============================================================================
        # RESEARCH INSTITUTES AND FOUNDATIONS
        # =============================================================================
        
        # Science for Africa Foundation (SFA)
        self.sources['sfa'] = DataSourceConfig(
            source_id='sfa',
            name='Science for Africa Foundation (SFA)',
            category=SourceCategory.RESEARCH_INSTITUTE,
            geographic_scope=GeographicScope.CONTINENTAL,
            primary_language=SupportedLanguage.ENGLISH,
            base_url='https://scienceforafrica.org',
            rss_feeds=['https://scienceforafrica.org/feed'],
            search_pages=[
                'https://scienceforafrica.org/funding-opportunities',
                'https://scienceforafrica.org/programs'
            ],
            sector_focus=[SectorFocus.HEALTHCARE, SectorFocus.AGRICULTURE, SectorFocus.CLIMATE],
            target_countries=['ALL_AFRICA'],
            underserved_focus=True,
            women_focus=True,
            youth_focus=True,
            search_frequency_hours=12,
            priority_weight=1.7,
            description='Pan-African foundation supporting scientific research and innovation'
        )
        
        # Mastercard Foundation
        self.sources['mastercard_foundation'] = DataSourceConfig(
            source_id='mastercard_foundation',
            name='Mastercard Foundation',
            category=SourceCategory.FOUNDATION,
            geographic_scope=GeographicScope.CONTINENTAL,
            primary_language=SupportedLanguage.ENGLISH,
            secondary_languages=[SupportedLanguage.FRENCH],
            base_url='https://mastercardfd.org',
            rss_feeds=['https://mastercardfd.org/feed'],
            search_pages=[
                'https://mastercardfd.org/funding-opportunities',
                'https://mastercardfd.org/programs'
            ],
            sector_focus=[SectorFocus.FINTECH, SectorFocus.EDUCATION, SectorFocus.AGRICULTURE],
            target_countries=['ALL_AFRICA'],
            underserved_focus=True,
            women_focus=True,
            youth_focus=True,
            rural_focus=True,
            search_frequency_hours=12,
            priority_weight=1.8,
            description='Focus on financial inclusion and youth empowerment in Africa'
        )
        
        # =============================================================================
        # REGIONAL ECONOMIC COMMUNITIES
        # =============================================================================
        
        # Economic Community of West African States (ECOWAS)
        self.sources['ecowas'] = DataSourceConfig(
            source_id='ecowas',
            name='Economic Community of West African States (ECOWAS)',
            category=SourceCategory.REGIONAL_ORGANIZATION,
            geographic_scope=GeographicScope.REGIONAL,
            primary_language=SupportedLanguage.ENGLISH,
            secondary_languages=[SupportedLanguage.FRENCH],
            base_url='https://ecowas.int',
            rss_feeds=['https://ecowas.int/feed'],
            search_pages=[
                'https://ecowas.int/funding',
                'https://ecowas.int/programs'
            ],
            sector_focus=[SectorFocus.INFRASTRUCTURE, SectorFocus.AGRICULTURE, SectorFocus.GENERAL_TECH],
            target_countries=['BJ', 'BF', 'CV', 'CI', 'GM', 'GH', 'GN', 'GW', 'LR', 'ML', 'NE', 'NG', 'SN', 'SL', 'TG'],
            underserved_focus=True,
            search_frequency_hours=24,
            priority_weight=1.4,
            description='West African regional organization with development programs'
        )
        
        # East African Community (EAC)
        self.sources['eac'] = DataSourceConfig(
            source_id='eac',
            name='East African Community (EAC)',
            category=SourceCategory.REGIONAL_ORGANIZATION,
            geographic_scope=GeographicScope.REGIONAL,
            primary_language=SupportedLanguage.ENGLISH,
            secondary_languages=[SupportedLanguage.SWAHILI],
            base_url='https://eac.int',
            rss_feeds=['https://eac.int/feed'],
            search_pages=[
                'https://eac.int/funding',
                'https://eac.int/programs'
            ],
            sector_focus=[SectorFocus.INFRASTRUCTURE, SectorFocus.AGRICULTURE, SectorFocus.GENERAL_TECH],
            target_countries=['BI', 'KE', 'RW', 'SS', 'TZ', 'UG'],
            underserved_focus=True,
            search_frequency_hours=24,
            priority_weight=1.3,
            description='East African regional organization with integration programs'
        )
        
        # Southern African Development Community (SADC)
        self.sources['sadc'] = DataSourceConfig(
            source_id='sadc',
            name='Southern African Development Community (SADC)',
            category=SourceCategory.REGIONAL_ORGANIZATION,
            geographic_scope=GeographicScope.REGIONAL,
            primary_language=SupportedLanguage.ENGLISH,
            secondary_languages=[SupportedLanguage.PORTUGUESE],
            base_url='https://sadc.int',
            rss_feeds=['https://sadc.int/feed'],
            search_pages=[
                'https://sadc.int/funding',
                'https://sadc.int/programmes'
            ],
            sector_focus=[SectorFocus.INFRASTRUCTURE, SectorFocus.AGRICULTURE, SectorFocus.CLIMATE],
            target_countries=['AO', 'BW', 'CD', 'SZ', 'LS', 'MG', 'MW', 'MU', 'MZ', 'NA', 'SC', 'ZA', 'TZ', 'ZM', 'ZW'],
            underserved_focus=True,
            search_frequency_hours=24,
            priority_weight=1.3,
            description='Southern African regional organization with development programs'
        )
        
        # =============================================================================
        # INNOVATION HUBS AND ACCELERATORS
        # =============================================================================
        
        # iHub (Kenya)
        self.sources['ihub_kenya'] = DataSourceConfig(
            source_id='ihub_kenya',
            name='iHub Kenya',
            category=SourceCategory.INNOVATION_HUB,
            geographic_scope=GeographicScope.NATIONAL,
            primary_language=SupportedLanguage.ENGLISH,
            base_url='https://ihub.co.ke',
            rss_feeds=['https://ihub.co.ke/feed'],
            search_pages=[
                'https://ihub.co.ke/programs',
                'https://ihub.co.ke/funding'
            ],
            sector_focus=[SectorFocus.GENERAL_TECH, SectorFocus.FINTECH, SectorFocus.HEALTHCARE],
            target_countries=['KE'],
            youth_focus=True,
            search_frequency_hours=24,
            priority_weight=1.2,
            description='Leading innovation hub in East Africa'
        )
        
        # Co-Creation Hub (Nigeria)
        self.sources['cchub_nigeria'] = DataSourceConfig(
            source_id='cchub_nigeria',
            name='Co-Creation Hub (CcHUB)',
            category=SourceCategory.INNOVATION_HUB,
            geographic_scope=GeographicScope.NATIONAL,
            primary_language=SupportedLanguage.ENGLISH,
            base_url='https://cchub.co',
            rss_feeds=['https://cchub.co/feed'],
            search_pages=[
                'https://cchub.co/programs',
                'https://cchub.co/funding'
            ],
            sector_focus=[SectorFocus.GENERAL_TECH, SectorFocus.FINTECH, SectorFocus.HEALTHCARE],
            target_countries=['NG'],
            youth_focus=True,
            search_frequency_hours=24,
            priority_weight=1.2,
            description='Leading innovation hub in West Africa'
        )
        
        # CIPESA (Uganda) - Collaboration on International ICT Policy for East and Southern Africa
        self.sources['cipesa_uganda'] = DataSourceConfig(
            source_id='cipesa_uganda',
            name='CIPESA Uganda',
            category=SourceCategory.RESEARCH_INSTITUTE,
            geographic_scope=GeographicScope.REGIONAL,
            primary_language=SupportedLanguage.ENGLISH,
            base_url='https://cipesa.org',
            rss_feeds=['https://cipesa.org/feed'],
            search_pages=[
                'https://cipesa.org/funding',
                'https://cipesa.org/programs'
            ],
            sector_focus=[SectorFocus.GENERAL_TECH, SectorFocus.EDUCATION],
            target_countries=['UG', 'KE', 'TZ', 'RW', 'ZM', 'ZW'],
            underserved_focus=True,
            search_frequency_hours=24,
            priority_weight=1.4,
            description='ICT policy research and capacity building in East/Southern Africa'
        )
        
        # =============================================================================
        # NATIONAL AI STRATEGY SOURCES
        # =============================================================================
        
        # Rwanda Development Board
        self.sources['rdb_rwanda'] = DataSourceConfig(
            source_id='rdb_rwanda',
            name='Rwanda Development Board',
            category=SourceCategory.GOVERNMENT_AGENCY,
            geographic_scope=GeographicScope.NATIONAL,
            primary_language=SupportedLanguage.ENGLISH,
            secondary_languages=[SupportedLanguage.FRENCH],
            base_url='https://rdb.rw',
            rss_feeds=['https://rdb.rw/feed'],
            search_pages=[
                'https://rdb.rw/funding',
                'https://rdb.rw/innovation'
            ],
            sector_focus=[SectorFocus.GENERAL_TECH, SectorFocus.HEALTHCARE, SectorFocus.FINTECH],
            target_countries=['RW'],
            underserved_focus=True,
            women_focus=True,
            youth_focus=True,
            search_frequency_hours=24,
            priority_weight=1.5,
            description='Rwanda national development agency with strong AI focus'
        )
        
        # Ghana Investment Promotion Centre
        self.sources['gipc_ghana'] = DataSourceConfig(
            source_id='gipc_ghana',
            name='Ghana Investment Promotion Centre',
            category=SourceCategory.GOVERNMENT_AGENCY,
            geographic_scope=GeographicScope.NATIONAL,
            primary_language=SupportedLanguage.ENGLISH,
            base_url='https://gipc.gov.gh',
            search_pages=[
                'https://gipc.gov.gh/funding',
                'https://gipc.gov.gh/programs'
            ],
            sector_focus=[SectorFocus.GENERAL_TECH, SectorFocus.AGRICULTURE, SectorFocus.FINTECH],
            target_countries=['GH'],
            women_focus=True,
            youth_focus=True,
            search_frequency_hours=24,
            priority_weight=1.3,
            description='Ghana national investment promotion with tech focus'
        )
        
        # =============================================================================
        # SPECIALIZED FUNDING SOURCES
        # =============================================================================
        
        # NEPAD (African Union Development Agency)
        self.sources['nepad'] = DataSourceConfig(
            source_id='nepad',
            name='NEPAD (African Union Development Agency)',
            category=SourceCategory.REGIONAL_ORGANIZATION,
            geographic_scope=GeographicScope.CONTINENTAL,
            primary_language=SupportedLanguage.ENGLISH,
            secondary_languages=[SupportedLanguage.FRENCH, SupportedLanguage.ARABIC],
            base_url='https://nepad.org',
            rss_feeds=['https://nepad.org/feed'],
            search_pages=[
                'https://nepad.org/funding',
                'https://nepad.org/programmes'
            ],
            sector_focus=[SectorFocus.HEALTHCARE, SectorFocus.AGRICULTURE, SectorFocus.INFRASTRUCTURE],
            target_countries=['ALL_AFRICA'],
            underserved_focus=True,
            women_focus=True,
            youth_focus=True,
            search_frequency_hours=12,
            priority_weight=1.8,
            description='African Union development agency with continental programs'
        )
        
        # Islamic Development Bank (IsDB)
        self.sources['isdb'] = DataSourceConfig(
            source_id='isdb',
            name='Islamic Development Bank (IsDB)',
            category=SourceCategory.MULTILATERAL_BANK,
            geographic_scope=GeographicScope.REGIONAL,
            primary_language=SupportedLanguage.ARABIC,
            secondary_languages=[SupportedLanguage.ENGLISH, SupportedLanguage.FRENCH],
            base_url='https://isdb.org',
            rss_feeds=['https://isdb.org/feed'],
            search_pages=[
                'https://isdb.org/funding',
                'https://isdb.org/programmes'
            ],
            sector_focus=[SectorFocus.HEALTHCARE, SectorFocus.AGRICULTURE, SectorFocus.EDUCATION],
            target_countries=['DZ', 'TD', 'DJ', 'EG', 'GM', 'GN', 'LY', 'ML', 'MR', 'MA', 'NE', 'NG', 'SN', 'SL', 'SO', 'SD', 'TN', 'UG'],
            underserved_focus=True,
            women_focus=True,
            search_frequency_hours=24,
            priority_weight=1.6,
            description='Islamic development bank serving African member countries'
        )
        
        # Gates Foundation Africa
        self.sources['gates_africa'] = DataSourceConfig(
            source_id='gates_africa',
            name='Bill & Melinda Gates Foundation Africa',
            category=SourceCategory.FOUNDATION,
            geographic_scope=GeographicScope.CONTINENTAL,
            primary_language=SupportedLanguage.ENGLISH,
            base_url='https://gatesfoundation.org',
            rss_feeds=['https://gatesfoundation.org/feed'],
            search_pages=[
                'https://gatesfoundation.org/funding-opportunities',
                'https://gatesfoundation.org/our-work/regions/africa'
            ],
            sector_focus=[SectorFocus.HEALTHCARE, SectorFocus.AGRICULTURE, SectorFocus.EDUCATION],
            target_countries=['ALL_AFRICA'],
            underserved_focus=True,
            women_focus=True,
            rural_focus=True,
            search_frequency_hours=12,
            priority_weight=1.7,
            description='Major foundation with significant African health and agriculture programs'
        )
        
        # =============================================================================
        # VENTURE CAPITAL AND PRIVATE SECTOR
        # =============================================================================
        
        # AfricArena
        self.sources['africarena'] = DataSourceConfig(
            source_id='africarena',
            name='AfricArena',
            category=SourceCategory.VENTURE_FUND,
            geographic_scope=GeographicScope.CONTINENTAL,
            primary_language=SupportedLanguage.ENGLISH,
            secondary_languages=[SupportedLanguage.FRENCH],
            base_url='https://africarena.com',
            rss_feeds=['https://africarena.com/feed'],
            search_pages=[
                'https://africarena.com/funding',
                'https://africarena.com/startups'
            ],
            sector_focus=[SectorFocus.GENERAL_TECH, SectorFocus.FINTECH, SectorFocus.HEALTHCARE],
            target_countries=['ALL_AFRICA'],
            youth_focus=True,
            search_frequency_hours=24,
            priority_weight=1.3,
            description='Pan-African startup ecosystem platform and funding network'
        )
        
        # Catalyst Fund
        self.sources['catalyst_fund'] = DataSourceConfig(
            source_id='catalyst_fund',
            name='Catalyst Fund',
            category=SourceCategory.VENTURE_FUND,
            geographic_scope=GeographicScope.CONTINENTAL,
            primary_language=SupportedLanguage.ENGLISH,
            base_url='https://catalyst.fund',
            rss_feeds=['https://catalyst.fund/feed'],
            search_pages=[
                'https://catalyst.fund/funding',
                'https://catalyst.fund/apply'
            ],
            sector_focus=[SectorFocus.FINTECH, SectorFocus.HEALTHCARE, SectorFocus.AGRICULTURE],
            target_countries=['ALL_AFRICA'],
            underserved_focus=True,
            women_focus=True,
            rural_focus=True,
            search_frequency_hours=12,
            priority_weight=1.6,
            description='Inclusive fintech accelerator focused on underserved populations'
        )