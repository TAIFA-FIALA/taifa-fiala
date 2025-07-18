"""
Multi-Language Source Discovery for African AI Funding
======================================================

Enhanced search capabilities for discovering intelligence feed
in multiple African languages, addressing the English-language bias
in current funding discovery systems.

Supports: French, Arabic, Portuguese, Swahili, Amharic, and Hausa
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import re
import json
import aiohttp
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# MULTILINGUAL MODELS
# =============================================================================

class SupportedLanguage(Enum):
    """Supported languages for multilingual search"""
    FRENCH = "fr"
    ARABIC = "ar"
    PORTUGUESE = "pt"
    SWAHILI = "sw"
    AMHARIC = "am"
    HAUSA = "ha"
    ENGLISH = "en"

class RegionalLanguageMapping(Enum):
    """Regional language mappings for targeted searches"""
    FRANCOPHONE_AFRICA = ["fr", "en"]  # West/Central Africa
    ANGLOPHONE_AFRICA = ["en", "sw"]   # East Africa
    LUSOPHONE_AFRICA = ["pt", "en"]    # Portuguese-speaking Africa
    NORTH_AFRICA = ["ar", "fr", "en"]  # North Africa
    HORN_OF_AFRICA = ["am", "ar", "en"] # Ethiopia, Somalia, etc.
    WEST_AFRICA = ["ha", "fr", "en"]   # Nigeria, Niger, etc.

@dataclass
class MultilingualQuery:
    """Multilingual search query"""
    base_query: str
    language: SupportedLanguage
    region_focus: Optional[str] = None
    sector_focus: Optional[str] = None
    translated_query: Optional[str] = None
    cultural_context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'base_query': self.base_query,
            'language': self.language.value,
            'region_focus': self.region_focus,
            'sector_focus': self.sector_focus,
            'translated_query': self.translated_query,
            'cultural_context': self.cultural_context
        }

@dataclass
class MultilingualSearchResult:
    """Result from multilingual search"""
    query: MultilingualQuery
    results: List[Dict[str, Any]]
    language_detected: Optional[str] = None
    confidence_score: float = 0.0
    cultural_relevance_score: float = 0.0
    translation_quality: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'query': self.query.to_dict(),
            'results_count': len(self.results),
            'language_detected': self.language_detected,
            'confidence_score': self.confidence_score,
            'cultural_relevance_score': self.cultural_relevance_score,
            'translation_quality': self.translation_quality,
            'results': self.results
        }

# =============================================================================
# MULTILINGUAL SEARCH QUERIES
# =============================================================================

class MultilingualQueryBank:
    """Bank of pre-crafted multilingual queries"""
    
    def __init__(self):
        self.query_templates = {
            SupportedLanguage.FRENCH: {
                'general_funding': [
                    'financement intelligence artificielle Afrique',
                    'subventions IA Afrique francophone',
                    'appel à propositions technologie Afrique',
                    'fonds innovation numérique Afrique',
                    'investissement startup tech Afrique'
                ],
                'grants': [
                    'appel à propositions recherche IA',
                    'bourse recherche intelligence artificielle',
                    'subvention innovation technologique',
                    'programme financement recherche',
                    'concours innovation numérique'
                ],
                'healthcare': [
                    'financement santé numérique Afrique',
                    'innovation santé intelligence artificielle',
                    'technologie médicale Afrique',
                    'e-santé financement Afrique',
                    'IA diagnostic médical Afrique'
                ],
                'agriculture': [
                    'agriculture intelligente Afrique',
                    'technologie agricole financement',
                    'innovation agriculture numérique',
                    'agtech Afrique financement',
                    'agriculture de précision Afrique'
                ],
                'women_focused': [
                    'financement femmes entrepreneures Afrique',
                    'programme femmes innovation',
                    'entrepreneuriat féminin technologie',
                    'leadership féminin innovation',
                    'femmes dirigeantes tech Afrique'
                ],
                'youth_focused': [
                    'financement jeunes entrepreneurs',
                    'programme jeunesse innovation',
                    'startup jeunes Afrique',
                    'entrepreneuriat jeunesse tech',
                    'innovation jeunes leaders'
                ]
            },
            SupportedLanguage.ARABIC: {
                'general_funding': [
                    'تمويل الذكاء الاصطناعي أفريقيا',
                    'منح بحثية ذكاء اصطناعي',
                    'استثمار تكنولوجيا أفريقيا',
                    'تمويل الابتكار الرقمي',
                    'برامج دعم الشركات الناشئة'
                ],
                'grants': [
                    'منح البحث العلمي',
                    'برامج التمويل التقني',
                    'مسابقات الابتكار',
                    'جوائز التكنولوجيا',
                    'دعم البحث والتطوير'
                ],
                'healthcare': [
                    'تمويل الصحة الرقمية',
                    'تكنولوجيا طبية أفريقيا',
                    'ابتكار صحي ذكي',
                    'الذكاء الاصطناعي الطبي',
                    'الصحة الإلكترونية أفريقيا'
                ],
                'agriculture': [
                    'الزراعة الذكية أفريقيا',
                    'تكنولوجيا زراعية',
                    'الابتكار الزراعي',
                    'الزراعة الرقمية',
                    'تمويل القطاع الزراعي'
                ],
                'women_focused': [
                    'تمويل المرأة المقاولة',
                    'برامج دعم المرأة',
                    'ريادة الأعمال النسائية',
                    'القيادة النسائية التقنية',
                    'الابتكار النسائي'
                ],
                'youth_focused': [
                    'تمويل الشباب المقاول',
                    'برامج دعم الشباب',
                    'ريادة الأعمال الشبابية',
                    'ابتكار الشباب',
                    'قيادة شبابية تقنية'
                ]
            },
            SupportedLanguage.PORTUGUESE: {
                'general_funding': [
                    'financiamento inteligência artificial África',
                    'bolsas investigação IA África',
                    'investimento tecnologia África',
                    'fundo inovação digital',
                    'startup tech África financiamento'
                ],
                'grants': [
                    'bolsas investigação científica',
                    'programas financiamento técnico',
                    'concursos inovação',
                    'prémios tecnologia',
                    'apoio investigação desenvolvimento'
                ],
                'healthcare': [
                    'financiamento saúde digital',
                    'tecnologia médica África',
                    'inovação saúde inteligente',
                    'IA médica diagnóstico',
                    'e-saúde África'
                ],
                'agriculture': [
                    'agricultura inteligente África',
                    'tecnologia agrícola financiamento',
                    'inovação agricultura digital',
                    'agtech África',
                    'agricultura precisão'
                ],
                'women_focused': [
                    'financiamento mulheres empreendedoras',
                    'programas apoio mulheres',
                    'empreendedorismo feminino',
                    'liderança feminina tecnologia',
                    'inovação feminina'
                ],
                'youth_focused': [
                    'financiamento jovens empreendedores',
                    'programas juventude inovação',
                    'startups jovens África',
                    'empreendedorismo juvenil',
                    'liderança jovem tecnologia'
                ]
            },
            SupportedLanguage.SWAHILI: {
                'general_funding': [
                    'ufumuzi akili bandia Afrika',
                    'ruzuku utafiti teknolojia',
                    'uwekezaji teknolojia Afrika',
                    'mfuko uvumbuzi dijiti',
                    'biashara mpya teknolojia'
                ],
                'grants': [
                    'ruzuku utafiti sayansi',
                    'programu ufumuzi kiufundi',
                    'mashindano uvumbuzi',
                    'tuzo teknolojia',
                    'msaada utafiti maendeleo'
                ],
                'healthcare': [
                    'ufumuzi afya ya dijiti',
                    'teknolojia ya matibabu',
                    'uvumbuzi afya mahiri',
                    'akili bandia matibabu',
                    'afya ya kielektroniki'
                ],
                'agriculture': [
                    'kilimo mahiri Afrika',
                    'teknolojia ya kilimo',
                    'uvumbuzi kilimo cha dijiti',
                    'kilimo cha usahihi',
                    'ufumuzi kilimo'
                ]
            },
            SupportedLanguage.AMHARIC: {
                'general_funding': [
                    'ኣርቲፊሻል ኢንተሊጀንስ ፋይናንስ ኣፍሪካ',
                    'ቴክኖሎጂ ኢንቨስትመንት ኣፍሪካ',
                    'ዲጂታል ኢኖቬሽን ፋንድ',
                    'ስታርት ኣፕ ቴክ ፋይናንስ',
                    'ኢኖቬሽን ግራንት'
                ],
                'healthcare': [
                    'ዲጂታል ሄልዝ ፋይናንስ',
                    'ሜዲካል ቴክኖሎጂ ኣፍሪካ',
                    'ስማርት ሄልዝ ኢኖቬሽን',
                    'ኤአይ ሜዲካል ዳይኣግኖሲስ',
                    'ኢ-ሄልዝ ኣፍሪካ'
                ],
                'agriculture': [
                    'ስማርት ኣግሪካልቸር ኣፍሪካ',
                    'ኣግሪካልቸር ቴክኖሎጂ',
                    'ዲጂታል ፋርሚንግ ኢኖቬሽን',
                    'ፕረሲዚን ኣግሪካልቸር',
                    'ኣግሪቴክ ኣፍሪካ'
                ]
            },
            SupportedLanguage.HAUSA: {
                'general_funding': [
                    'kudade fasaha ta wucin gadi Afrika',
                    'tallafi bincike fasaha',
                    'saka hannun jari fasaha Afrika',
                    'asusun kirkire-kirkire na dijital',
                    'tallafin kasuwanci na fasaha'
                ],
                'healthcare': [
                    'kudade lafiya ta dijital',
                    'fasaha ta likitanci Afrika',
                    'kirkire-kirkire na lafiya',
                    'fasaha ta wucin gadi ta likitanci',
                    'lafiya ta lantarki Afrika'
                ],
                'agriculture': [
                    'aikin gona na fasaha Afrika',
                    'fasaha ta aikin gona',
                    'kirkire-kirkire na aikin gona',
                    'aikin gona na dijital',
                    'tallafin fannin noma'
                ]
            }
        }
        
        # Regional search preferences
        self.regional_preferences = {
            'central_africa': [SupportedLanguage.FRENCH, SupportedLanguage.ENGLISH],
            'west_africa': [SupportedLanguage.FRENCH, SupportedLanguage.ENGLISH, SupportedLanguage.HAUSA],
            'east_africa': [SupportedLanguage.ENGLISH, SupportedLanguage.SWAHILI, SupportedLanguage.AMHARIC],
            'north_africa': [SupportedLanguage.ARABIC, SupportedLanguage.FRENCH, SupportedLanguage.ENGLISH],
            'southern_africa': [SupportedLanguage.ENGLISH, SupportedLanguage.PORTUGUESE],
            'horn_of_africa': [SupportedLanguage.AMHARIC, SupportedLanguage.ARABIC, SupportedLanguage.ENGLISH]
        }
    
    def get_queries_for_language(self, language: SupportedLanguage, category: str = 'general_funding') -> List[str]:
        """Get queries for a specific language and category"""
        return self.query_templates.get(language, {}).get(category, [])
    
    def get_regional_languages(self, region: str) -> List[SupportedLanguage]:
        """Get preferred languages for a region"""
        return self.regional_preferences.get(region, [SupportedLanguage.ENGLISH])
    
    def get_all_categories(self) -> List[str]:
        """Get all available query categories"""
        return list(next(iter(self.query_templates.values())).keys())

# =============================================================================
# MULTILINGUAL SEARCH ENGINE
# =============================================================================

class MultilingualSearchEngine:
    """Engine for multilingual intelligence item discovery"""
    
    def __init__(self, serper_api_key: str):
        self.serper_api_key = serper_api_key
        self.logger = logging.getLogger(__name__)
        self.query_bank = MultilingualQueryBank()
        
        # Search configuration
        self.search_config = {
            'num_results': 20,
            'timeout': 30,
            'rate_limit_delay': 1.0,
            'max_retries': 3
        }
        
        # Language detection patterns
        self.language_patterns = {
            SupportedLanguage.FRENCH: [
                r'financement|subvention|appel|propositions|recherche|innovation',
                r'programme|concours|bourse|développement|technologie'
            ],
            SupportedLanguage.ARABIC: [
                r'تمويل|منح|برامج|دعم|ابتكار|تكنولوجيا',
                r'استثمار|تطوير|بحث|مسابقات|جوائز'
            ],
            SupportedLanguage.PORTUGUESE: [
                r'financiamento|bolsas|investigação|inovação|tecnologia',
                r'programas|concursos|apoio|desenvolvimento|empreendedorismo'
            ],
            SupportedLanguage.SWAHILI: [
                r'ufumuzi|ruzuku|utafiti|teknolojia|uvumbuzi',
                r'programu|mashindano|msaada|maendeleo|biashara'
            ],
            SupportedLanguage.AMHARIC: [
                r'ፋይናንስ|ግራንት|ቴክኖሎጂ|ኢኖቬሽን',
                r'ፕሮግራም|ዲቨሎፕመንት|ርሰርች|ስታርት'
            ],
            SupportedLanguage.HAUSA: [
                r'kudade|tallafi|bincike|fasaha|kirkire',
                r'shirye|gasa|ci|bunkasa|kasuwanci'
            ]
        }
    
    async def search_multilingual(self, base_query: str, target_languages: List[SupportedLanguage], 
                                 region_focus: Optional[str] = None, 
                                 sector_focus: Optional[str] = None) -> List[MultilingualSearchResult]:
        """Perform multilingual search across specified languages"""
        results = []
        
        try:
            # Create search tasks for each language
            search_tasks = []
            for language in target_languages:
                # Get language-specific queries
                queries = self._generate_language_queries(base_query, language, sector_focus)
                
                for query_text in queries:
                    multilingual_query = MultilingualQuery(
                        base_query=base_query,
                        language=language,
                        region_focus=region_focus,
                        sector_focus=sector_focus,
                        translated_query=query_text
                    )
                    
                    search_tasks.append(self._search_single_language(multilingual_query))
            
            # Execute searches concurrently
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Process results
            for result in search_results:
                if isinstance(result, Exception):
                    self.logger.error(f"Search failed: {result}")
                    continue
                
                if isinstance(result, MultilingualSearchResult):
                    results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Multilingual search failed: {e}")
            return []
    
    async def search_by_region(self, base_query: str, region: str, 
                              sector_focus: Optional[str] = None) -> List[MultilingualSearchResult]:
        """Search using region-appropriate languages"""
        target_languages = self.query_bank.get_regional_languages(region)
        return await self.search_multilingual(base_query, target_languages, region, sector_focus)
    
    async def comprehensive_african_search(self, base_query: str, 
                                         sector_focus: Optional[str] = None) -> Dict[str, List[MultilingualSearchResult]]:
        """Comprehensive search across all African regions and languages"""
        regional_results = {}
        
        regions = [
            'central_africa', 'west_africa', 'east_africa', 
            'north_africa', 'southern_africa', 'horn_of_africa'
        ]
        
        # Search each region
        for region in regions:
            try:
                results = await self.search_by_region(base_query, region, sector_focus)
                regional_results[region] = results
            except Exception as e:
                self.logger.error(f"Regional search failed for {region}: {e}")
                regional_results[region] = []
        
        return regional_results
    
    async def _search_single_language(self, query: MultilingualQuery) -> MultilingualSearchResult:
        """Execute search for a single language query"""
        try:
            # Prepare search parameters
            search_params = {
                'q': query.translated_query,
                'num': self.search_config['num_results'],
                'hl': query.language.value,
                'gl': self._get_country_code_for_language(query.language),
                'type': 'search'
            }
            
            # Add regional focus if specified
            if query.region_focus:
                search_params['q'] += f' site:{self._get_regional_domains(query.region_focus)}'
            
            # Execute search
            search_results = await self._execute_serper_search(search_params)
            
            # Process and score results
            processed_results = await self._process_search_results(search_results, query)
            
            # Calculate relevance scores
            confidence_score = await self._calculate_confidence_score(processed_results, query)
            cultural_relevance = await self._calculate_cultural_relevance(processed_results, query)
            
            return MultilingualSearchResult(
                query=query,
                results=processed_results,
                language_detected=query.language.value,
                confidence_score=confidence_score,
                cultural_relevance_score=cultural_relevance,
                translation_quality=await self._assess_translation_quality(query)
            )
            
        except Exception as e:
            self.logger.error(f"Single language search failed: {e}")
            return MultilingualSearchResult(
                query=query,
                results=[],
                confidence_score=0.0
            )
    
    async def _execute_serper_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search using Serper API"""
        try:
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://google.serper.dev/search',
                    headers=headers,
                    json=params,
                    timeout=aiohttp.ClientTimeout(total=self.search_config['timeout'])
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Serper API error: {response.status}")
                        return {}
            
        except Exception as e:
            self.logger.error(f"Serper search execution failed: {e}")
            return {}   