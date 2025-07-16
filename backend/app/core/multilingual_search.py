"""
Multi-Language Source Discovery for African AI Funding
======================================================

Enhanced search capabilities for discovering funding opportunities
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
    """Engine for multilingual funding opportunity discovery"""
    
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
                        return {}\n            \n        except Exception as e:\n            self.logger.error(f\"Serper search execution failed: {e}\")\n            return {}\n    \n    async def _process_search_results(self, search_results: Dict[str, Any], \n                                     query: MultilingualQuery) -> List[Dict[str, Any]]:\n        \"\"\"Process and enhance search results\"\"\"\n        processed_results = []\n        \n        try:\n            organic_results = search_results.get('organic', [])\n            \n            for result in organic_results:\n                # Extract basic information\n                processed_result = {\n                    'title': result.get('title', ''),\n                    'description': result.get('snippet', ''),\n                    'url': result.get('link', ''),\n                    'source': result.get('source', ''),\n                    'date': result.get('date', ''),\n                    'language': query.language.value,\n                    'region_focus': query.region_focus,\n                    'sector_focus': query.sector_focus\n                }\n                \n                # Add multilingual metadata\n                processed_result['multilingual_metadata'] = {\n                    'original_query': query.base_query,\n                    'translated_query': query.translated_query,\n                    'language_detected': await self._detect_content_language(result),\n                    'cultural_indicators': await self._detect_cultural_indicators(result, query.language),\n                    'regional_relevance': await self._assess_regional_relevance(result, query.region_focus)\n                }\n                \n                processed_results.append(processed_result)\n            \n            return processed_results\n            \n        except Exception as e:\n            self.logger.error(f\"Processing search results failed: {e}\")\n            return []\n    \n    def _generate_language_queries(self, base_query: str, language: SupportedLanguage, \n                                 sector_focus: Optional[str] = None) -> List[str]:\n        \"\"\"Generate language-specific queries\"\"\"\n        try:\n            # Get base queries for the language\n            category = sector_focus if sector_focus in self.query_bank.get_all_categories() else 'general_funding'\n            base_queries = self.query_bank.get_queries_for_language(language, category)\n            \n            # If no pre-defined queries, use translated base query\n            if not base_queries:\n                base_queries = [base_query]  # In production, would use translation service\n            \n            # Enhance queries with regional and sector terms\n            enhanced_queries = []\n            for query in base_queries[:3]:  # Limit to top 3 queries\n                enhanced_query = query\n                \n                # Add sector-specific terms\n                if sector_focus:\n                    sector_terms = self._get_sector_terms(sector_focus, language)\n                    enhanced_query += f' {sector_terms}'\n                \n                enhanced_queries.append(enhanced_query)\n            \n            return enhanced_queries\n            \n        except Exception as e:\n            self.logger.error(f\"Generating language queries failed: {e}\")\n            return [base_query]\n    \n    def _get_sector_terms(self, sector: str, language: SupportedLanguage) -> str:\n        \"\"\"Get sector-specific terms in the target language\"\"\"\n        sector_terms = {\n            SupportedLanguage.FRENCH: {\n                'healthcare': 'santé numérique e-santé',\n                'agriculture': 'agriculture numérique agtech',\n                'education': 'éducation numérique edtech',\n                'fintech': 'technologie financière fintech',\n                'climate': 'climat environnement durable'\n            },\n            SupportedLanguage.ARABIC: {\n                'healthcare': 'الصحة الرقمية التكنولوجيا الطبية',\n                'agriculture': 'الزراعة الرقمية التكنولوجيا الزراعية',\n                'education': 'التعليم الرقمي التكنولوجيا التعليمية',\n                'fintech': 'التكنولوجيا المالية الخدمات المصرفية',\n                'climate': 'المناخ البيئة الاستدامة'\n            },\n            SupportedLanguage.PORTUGUESE: {\n                'healthcare': 'saúde digital e-saúde',\n                'agriculture': 'agricultura digital agtech',\n                'education': 'educação digital edtech',\n                'fintech': 'tecnologia financeira fintech',\n                'climate': 'clima ambiente sustentável'\n            }\n        }\n        \n        return sector_terms.get(language, {}).get(sector, '')\n    \n    def _get_country_code_for_language(self, language: SupportedLanguage) -> str:\n        \"\"\"Get appropriate country code for language targeting\"\"\"\n        country_codes = {\n            SupportedLanguage.FRENCH: 'sn',  # Senegal\n            SupportedLanguage.ARABIC: 'eg',  # Egypt\n            SupportedLanguage.PORTUGUESE: 'ao',  # Angola\n            SupportedLanguage.SWAHILI: 'ke',  # Kenya\n            SupportedLanguage.AMHARIC: 'et',  # Ethiopia\n            SupportedLanguage.HAUSA: 'ng',  # Nigeria\n            SupportedLanguage.ENGLISH: 'za'  # South Africa\n        }\n        \n        return country_codes.get(language, 'za')\n    \n    def _get_regional_domains(self, region: str) -> str:\n        \"\"\"Get regional domain patterns for site filtering\"\"\"\n        regional_domains = {\n            'central_africa': 'site:.cf OR site:.td OR site:.cd OR site:.cm',\n            'west_africa': 'site:.ng OR site:.gh OR site:.sn OR site:.ci',\n            'east_africa': 'site:.ke OR site:.tz OR site:.ug OR site:.rw',\n            'north_africa': 'site:.eg OR site:.ma OR site:.tn OR site:.dz',\n            'southern_africa': 'site:.za OR site:.bw OR site:.na OR site:.zw',\n            'horn_of_africa': 'site:.et OR site:.so OR site:.dj OR site:.er'\n        }\n        \n        return regional_domains.get(region, '')\n    \n    async def _detect_content_language(self, result: Dict[str, Any]) -> str:\n        \"\"\"Detect the language of search result content\"\"\"\n        content = f\"{result.get('title', '')} {result.get('snippet', '')}\"\n        \n        # Simple language detection using patterns\n        for language, patterns in self.language_patterns.items():\n            for pattern in patterns:\n                if re.search(pattern, content, re.IGNORECASE):\n                    return language.value\n        \n        return 'unknown'\n    \n    async def _detect_cultural_indicators(self, result: Dict[str, Any], \n                                        language: SupportedLanguage) -> List[str]:\n        \"\"\"Detect cultural indicators in search results\"\"\"\n        indicators = []\n        content = f\"{result.get('title', '')} {result.get('snippet', '')}\"\n        \n        # Cultural patterns by language\n        cultural_patterns = {\n            SupportedLanguage.FRENCH: {\n                'francophone_focus': r'francophone|afrique francophone|CEDEAO',\n                'development_focus': r'développement|coopération|AFD',\n                'regional_org': r'UEMOA|CEMAC|OIF'\n            },\n            SupportedLanguage.ARABIC: {\n                'arab_focus': r'العربية|المغرب العربي|الجامعة العربية',\n                'islamic_focus': r'إسلامي|البنك الإسلامي|التنمية الإسلامية',\n                'regional_org': r'اتحاد المغرب العربي|جامعة الدول العربية'\n            },\n            SupportedLanguage.PORTUGUESE: {\n                'lusophone_focus': r'lusófono|PALOP|CPLP',\n                'development_focus': r'desenvolvimento|cooperação',\n                'regional_org': r'SADC|CPLP|União Africana'\n            }\n        }\n        \n        patterns = cultural_patterns.get(language, {})\n        for indicator, pattern in patterns.items():\n            if re.search(pattern, content, re.IGNORECASE):\n                indicators.append(indicator)\n        \n        return indicators\n    \n    async def _assess_regional_relevance(self, result: Dict[str, Any], \n                                       region_focus: Optional[str]) -> float:\n        \"\"\"Assess regional relevance of search result\"\"\"\n        if not region_focus:\n            return 0.5\n        \n        content = f\"{result.get('title', '')} {result.get('snippet', '')}\"\n        \n        # Regional keywords\n        regional_keywords = {\n            'central_africa': ['central africa', 'afrique centrale', 'CEMAC', 'ECCAS'],\n            'west_africa': ['west africa', 'afrique ouest', 'ECOWAS', 'CEDEAO'],\n            'east_africa': ['east africa', 'afrique est', 'EAC', 'CAE'],\n            'north_africa': ['north africa', 'afrique nord', 'maghreb', 'المغرب'],\n            'southern_africa': ['southern africa', 'afrique australe', 'SADC'],\n            'horn_of_africa': ['horn of africa', 'corne afrique', 'IGAD']\n        }\n        \n        keywords = regional_keywords.get(region_focus, [])\n        relevance_score = 0.0\n        \n        for keyword in keywords:\n            if keyword.lower() in content.lower():\n                relevance_score += 0.25\n        \n        return min(1.0, relevance_score)\n    \n    async def _calculate_confidence_score(self, results: List[Dict[str, Any]], \n                                        query: MultilingualQuery) -> float:\n        \"\"\"Calculate confidence score for search results\"\"\"\n        if not results:\n            return 0.0\n        \n        # Calculate based on result quality and language match\n        quality_scores = []\n        \n        for result in results:\n            score = 0.0\n            \n            # Language match\n            detected_lang = result.get('multilingual_metadata', {}).get('language_detected', '')\n            if detected_lang == query.language.value:\n                score += 0.3\n            \n            # Regional relevance\n            regional_score = result.get('multilingual_metadata', {}).get('regional_relevance', 0)\n            score += regional_score * 0.2\n            \n            # Cultural indicators\n            cultural_indicators = result.get('multilingual_metadata', {}).get('cultural_indicators', [])\n            if cultural_indicators:\n                score += min(0.3, len(cultural_indicators) * 0.1)\n            \n            # Content quality (title and description length)\n            if len(result.get('title', '')) > 20:\n                score += 0.1\n            if len(result.get('description', '')) > 50:\n                score += 0.1\n            \n            quality_scores.append(score)\n        \n        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0\n    \n    async def _calculate_cultural_relevance(self, results: List[Dict[str, Any]], \n                                          query: MultilingualQuery) -> float:\n        \"\"\"Calculate cultural relevance score\"\"\"\n        if not results:\n            return 0.0\n        \n        cultural_scores = []\n        \n        for result in results:\n            cultural_indicators = result.get('multilingual_metadata', {}).get('cultural_indicators', [])\n            regional_relevance = result.get('multilingual_metadata', {}).get('regional_relevance', 0)\n            \n            # Cultural score based on indicators and regional relevance\n            cultural_score = (len(cultural_indicators) * 0.2) + (regional_relevance * 0.8)\n            cultural_scores.append(min(1.0, cultural_score))\n        \n        return sum(cultural_scores) / len(cultural_scores) if cultural_scores else 0.0\n    \n    async def _assess_translation_quality(self, query: MultilingualQuery) -> float:\n        \"\"\"Assess quality of query translation\"\"\"\n        # Simple heuristic - in production would use translation quality API\n        if query.translated_query and query.translated_query != query.base_query:\n            return 0.8  # Assume good translation\n        elif query.language == SupportedLanguage.ENGLISH:\n            return 1.0  # No translation needed\n        else:\n            return 0.5  # Unknown quality\n\n# =============================================================================\n# USAGE EXAMPLE\n# =============================================================================\n\nasync def example_usage():\n    \"\"\"Example usage of multilingual search engine\"\"\"\n    # Initialize search engine\n    search_engine = MultilingualSearchEngine(serper_api_key=\"your-api-key\")\n    \n    # Search for AI healthcare funding in French\n    french_results = await search_engine.search_multilingual(\n        base_query=\"AI healthcare funding Africa\",\n        target_languages=[SupportedLanguage.FRENCH],\n        region_focus=\"west_africa\",\n        sector_focus=\"healthcare\"\n    )\n    \n    print(\"French Search Results:\")\n    for result in french_results:\n        print(f\"Query: {result.query.translated_query}\")\n        print(f\"Results: {len(result.results)}\")\n        print(f\"Confidence: {result.confidence_score:.3f}\")\n        print(\"---\")\n    \n    # Comprehensive African search\n    comprehensive_results = await search_engine.comprehensive_african_search(\n        base_query=\"AI startup funding\",\n        sector_focus=\"general_funding\"\n    )\n    \n    print(\"\\nComprehensive African Search:\")\n    for region, results in comprehensive_results.items():\n        print(f\"{region}: {len(results)} result sets\")\n    \n    # Regional search for East Africa\n    east_africa_results = await search_engine.search_by_region(\n        base_query=\"agriculture technology funding\",\n        region=\"east_africa\",\n        sector_focus=\"agriculture\"\n    )\n    \n    print(f\"\\nEast Africa Results: {len(east_africa_results)} result sets\")\n\nif __name__ == \"__main__\":\n    asyncio.run(example_usage())"