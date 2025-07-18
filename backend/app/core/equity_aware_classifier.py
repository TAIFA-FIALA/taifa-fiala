"""
Equity-Aware Content Classification System
=========================================

Enhanced content classification system that actively combats systemic inequities
in African AI funding by prioritizing underserved regions, sectors, and populations.

Based on architecture review recommendations focusing on:
- Geographic bias detection and correction
- Sectoral alignment with development priorities
- Gender and inclusion signal detection
- Funding stage intelligence
- Transparency and equity scoring
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from statistics import mean

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# EQUITY-AWARE MODELS
# =============================================================================

class PriorityScore(Enum):
    """Priority scoring levels"""
    CRITICAL = 5.0    # Underserved regions + priority sectors
    HIGH = 4.0        # Underserved regions OR priority sectors
    ELEVATED = 3.0    # Inclusion-focused opportunities
    NORMAL = 2.0      # Standard opportunities
    LOW = 1.0         # Over-represented regions/sectors

class GeographicTier(Enum):
    """Geographic priority tiers based on funding concentration"""
    UNDERSERVED = "underserved"      # Central/West Africa, least funded
    EMERGING = "emerging"            # Growing but still underrepresented
    ESTABLISHED = "established"      # Moderate funding presence
    SATURATED = "saturated"         # Big 4 countries (KE, NG, ZA, EG)

class SectorPriority(Enum):
    """Sector priorities based on development needs"""
    CRITICAL = "critical"           # Healthcare, Agriculture, Climate
    HIGH = "high"                   # Education, Infrastructure
    MEDIUM = "medium"               # General tech, Business
    LOW = "low"                     # Over-represented sectors

class InclusionCategory(Enum):
    """Inclusion categories for targeted support"""
    WOMEN_LED = "women_led"
    YOUTH_FOCUSED = "youth_focused"
    RURAL_PRIORITY = "rural_priority"
    DISABILITY_INCLUSIVE = "disability_inclusive"
    REFUGEE_FOCUSED = "refugee_focused"

@dataclass
class EquityScore:
    """Comprehensive equity scoring"""
    geographic_score: float = 0.0
    sectoral_score: float = 0.0
    inclusion_score: float = 0.0
    stage_score: float = 0.0
    transparency_score: float = 0.0
    overall_priority: PriorityScore = PriorityScore.NORMAL
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall equity score"""
        weights = {
            'geographic': 0.30,
            'sectoral': 0.25,
            'inclusion': 0.20,
            'stage': 0.15,
            'transparency': 0.10
        }
        
        return (
            self.geographic_score * weights['geographic'] +
            self.sectoral_score * weights['sectoral'] +
            self.inclusion_score * weights['inclusion'] +
            self.stage_score * weights['stage'] +
            self.transparency_score * weights['transparency']
        )

@dataclass
class ClassificationResult:
    """Enhanced classification result with equity metrics"""
    content_type: str
    confidence_score: float
    equity_score: EquityScore
    priority_flags: List[str] = field(default_factory=list)
    detected_countries: List[str] = field(default_factory=list)
    detected_sectors: List[str] = field(default_factory=list)
    inclusion_indicators: List[InclusionCategory] = field(default_factory=list)
    funding_stage: Optional[str] = None
    transparency_issues: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'content_type': self.content_type,
            'confidence_score': self.confidence_score,
            'equity_score': {
                'geographic_score': self.equity_score.geographic_score,
                'sectoral_score': self.equity_score.sectoral_score,
                'inclusion_score': self.equity_score.inclusion_score,
                'stage_score': self.equity_score.stage_score,
                'transparency_score': self.equity_score.transparency_score,
                'overall_score': self.equity_score.calculate_overall_score(),
                'priority_level': self.equity_score.overall_priority.value
            },
            'priority_flags': self.priority_flags,
            'detected_countries': self.detected_countries,
            'detected_sectors': self.detected_sectors,
            'inclusion_indicators': [cat.value for cat in self.inclusion_indicators],
            'funding_stage': self.funding_stage,
            'transparency_issues': self.transparency_issues
        }

# =============================================================================
# GEOGRAPHIC BIAS DETECTION
# =============================================================================

class GeographicBiasDetector:
    """Detects and corrects geographic bias in intelligence feed"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Country classifications based on funding concentration data
        self.country_tiers = {
            GeographicTier.UNDERSERVED: {
                'central_africa': ['CF', 'TD', 'CD', 'CM', 'GQ', 'GA', 'ST', 'AO'],
                'west_africa': ['GW', 'SL', 'LR', 'TG', 'BJ', 'NE', 'ML', 'BF'],
                'horn_africa': ['ER', 'DJ', 'SO', 'SS'],
                'southern_africa': ['MZ', 'MW', 'ZM', 'ZW', 'SZ', 'LS']
            },
            GeographicTier.EMERGING: {
                'east_africa': ['UG', 'TZ', 'RW', 'BI', 'MG', 'KM', 'MU', 'SC'],
                'west_africa': ['SN', 'CI', 'GH', 'GM'],
                'north_africa': ['MA', 'TN', 'DZ', 'LY', 'SD']
            },
            GeographicTier.ESTABLISHED: {
                'regional_hubs': ['BW', 'NA', 'ET', 'CV'],
                'emerging_tech': ['MW', 'ZM']
            },
            GeographicTier.SATURATED: {
                'big_four': ['KE', 'NG', 'ZA', 'EG']
            }
        }
        
        # Flatten country mappings for quick lookup
        self.country_to_tier = {}
        for tier, regions in self.country_tiers.items():
            for region, countries in regions.items():
                for country in countries:
                    self.country_to_tier[country] = tier
        
        # Country name mappings (ISO code to common names)
        self.country_names = {
            'CF': ['Central African Republic', 'CAR'],
            'TD': ['Chad', 'Tchad'],
            'CD': ['Democratic Republic of Congo', 'DRC', 'Congo-Kinshasa'],
            'CM': ['Cameroon', 'Cameroun'],
            'GQ': ['Equatorial Guinea', 'Guinea Ecuatorial'],
            'GA': ['Gabon'],
            'KE': ['Kenya'],
            'NG': ['Nigeria'],
            'ZA': ['South Africa', 'RSA'],
            'EG': ['Egypt'],
            'GH': ['Ghana'],
            'ET': ['Ethiopia'],
            'UG': ['Uganda'],
            'TZ': ['Tanzania'],
            'RW': ['Rwanda'],
            'SN': ['Senegal'],
            'CI': ['Ivory Coast', 'Côte d\'Ivoire'],
            'MA': ['Morocco', 'Maroc'],
            'TN': ['Tunisia', 'Tunisie'],
            'BW': ['Botswana'],
            'NA': ['Namibia'],
            'MU': ['Mauritius'],
            'MW': ['Malawi'],
            'ZM': ['Zambia'],
            'ZW': ['Zimbabwe']
        }
        
        # Priority multipliers for geographic scoring
        self.tier_multipliers = {
            GeographicTier.UNDERSERVED: 2.0,
            GeographicTier.EMERGING: 1.5,
            GeographicTier.ESTABLISHED: 1.0,
            GeographicTier.SATURATED: 0.7
        }
    
    async def detect_countries(self, content: str) -> List[str]:
        """Detect mentioned countries in content"""
        detected_countries = []
        content_lower = content.lower()
        
        # Check for country mentions
        for iso_code, names in self.country_names.items():
            for name in names:
                if name.lower() in content_lower:
                    detected_countries.append(iso_code)
                    break
        
        # Check for regional mentions
        regional_patterns = {
            'central_africa': r'central\s+africa|afrique\s+centrale',
            'west_africa': r'west\s+africa|afrique\s+de\s+l\'ouest',
            'east_africa': r'east\s+africa|afrique\s+de\s+l\'est',
            'southern_africa': r'southern\s+africa|afrique\s+australe',
            'north_africa': r'north\s+africa|afrique\s+du\s+nord',
            'horn_africa': r'horn\s+of\s+africa|corne\s+de\s+l\'afrique',
            'sahel': r'sahel|sahélien',
            'maghreb': r'maghreb|maghrébin'
        }
        
        for region, pattern in regional_patterns.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                # Add representative countries from the region
                if region in ['central_africa', 'west_africa']:
                    detected_countries.extend(['CF', 'TD', 'CD', 'CM'])
                elif region == 'east_africa':
                    detected_countries.extend(['UG', 'TZ', 'RW', 'ET'])
                elif region == 'southern_africa':
                    detected_countries.extend(['BW', 'NA', 'ZW', 'ZM'])
                elif region == 'north_africa':
                    detected_countries.extend(['MA', 'TN', 'DZ', 'EG'])
        
        return list(set(detected_countries))  # Remove duplicates
    
    async def score_geographic_priority(self, detected_countries: List[str]) -> Tuple[float, PriorityScore]:
        """Score geographic priority based on detected countries"""
        if not detected_countries:
            return 0.5, PriorityScore.NORMAL
        
        # Calculate weighted score based on country tiers
        tier_scores = []
        priority_flags = []
        
        for country in detected_countries:
            tier = self.country_to_tier.get(country, GeographicTier.ESTABLISHED)
            multiplier = self.tier_multipliers[tier]
            tier_scores.append(multiplier)
            
            if tier == GeographicTier.UNDERSERVED:
                priority_flags.append(f"underserved_country_{country}")
            elif tier == GeographicTier.SATURATED:
                priority_flags.append(f"saturated_country_{country}")
        
        # Calculate average score
        geographic_score = mean(tier_scores) if tier_scores else 1.0
        
        # Determine priority level
        if geographic_score >= 1.8:
            priority = PriorityScore.CRITICAL
        elif geographic_score >= 1.4:
            priority = PriorityScore.HIGH
        elif geographic_score >= 1.1:
            priority = PriorityScore.ELEVATED
        elif geographic_score >= 0.9:
            priority = PriorityScore.NORMAL
        else:
            priority = PriorityScore.LOW
        
        return geographic_score, priority
    
    async def check_geographic_inclusion(self, content: str) -> Dict[str, Any]:
        """Check for geographic inclusion indicators"""
        inclusion_indicators = []
        content_lower = content.lower()
        
        # Regional inclusion patterns
        inclusion_patterns = {
            'multi_country': r'multi-country|cross-border|regional|pan-african',
            'rural_focus': r'rural|remote|off-grid|last mile|underserved communities',
            'conflict_areas': r'conflict|post-conflict|fragile|refugee|displaced',
            'landlocked': r'landlocked|enclavé|sans littoral'
        }
        
        for category, pattern in inclusion_patterns.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                inclusion_indicators.append(category)
        
        return {
            'inclusion_indicators': inclusion_indicators,
            'geographic_scope': 'regional' if 'multi_country' in inclusion_indicators else 'national'
        }

# =============================================================================
# SECTORAL ALIGNMENT DETECTION
# =============================================================================

class SectoralAlignmentDetector:
    """Detects sectoral alignment with African development priorities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Priority sector patterns based on development needs
        self.sector_patterns = {
            'healthcare': {
                'priority': SectorPriority.CRITICAL,
                'patterns': [
                    r'health|medical|disease|patient|clinic|hospital',
                    r'maternal|tuberculosis|malaria|epidemic|pandemic',
                    r'diagnosis|treatment|prevention|therapy',
                    r'telemedicine|healthtech|medtech|pharmaceutical',
                    r'nutrition|sanitation|hygiene|vaccination'
                ],
                'weight': 2.0
            },
            'agriculture': {
                'priority': SectorPriority.CRITICAL,
                'patterns': [
                    r'farming|agriculture|crop|livestock|agri-tech|agtech',
                    r'food security|yield|irrigation|pest|drought',
                    r'smallholder|rural farmer|subsistence|pastoral',
                    r'precision agriculture|smart farming|soil|climate-smart',
                    r'fisheries|aquaculture|forestry|agroforestry'
                ],
                'weight': 2.0
            },
            'climate': {
                'priority': SectorPriority.CRITICAL,
                'patterns': [
                    r'climate|environmental|sustainability|green|renewable',
                    r'carbon|emissions|adaptation|resilience|mitigation',
                    r'solar|wind|hydroelectric|geothermal|biomass',
                    r'waste management|circular economy|recycling',
                    r'biodiversity|conservation|ecosystem|deforestation'
                ],
                'weight': 2.0
            },
            'education': {
                'priority': SectorPriority.HIGH,
                'patterns': [
                    r'education|learning|teaching|school|university',
                    r'literacy|numeracy|skills|training|capacity building',
                    r'edtech|e-learning|digital learning|MOOC',
                    r'vocational|technical|STEM|research|academic'
                ],
                'weight': 1.5
            },
            'infrastructure': {
                'priority': SectorPriority.HIGH,
                'patterns': [
                    r'infrastructure|connectivity|broadband|internet|digital',
                    r'transportation|logistics|supply chain|mobility',
                    r'water|sanitation|energy|power|electricity',
                    r'telecommunications|5G|fiber optic|satellite',
                    r'smart city|urban planning|housing|construction'
                ],
                'weight': 1.5
            },
            'fintech': {
                'priority': SectorPriority.MEDIUM,
                'patterns': [
                    r'fintech|financial technology|mobile money|digital payment',
                    r'banking|credit|lending|insurance|investment',
                    r'blockchain|cryptocurrency|DeFi|digital currency',
                    r'remittance|cross-border payment|financial inclusion'
                ],
                'weight': 1.0
            },
            'general_tech': {
                'priority': SectorPriority.LOW,
                'patterns': [
                    r'technology|tech|software|app|platform|digital',
                    r'artificial intelligence|machine learning|AI|ML',
                    r'data science|analytics|big data|IoT',
                    r'startup|entrepreneur|innovation|venture'
                ],
                'weight': 0.8
            }
        }
    
    async def detect_sectors(self, content: str) -> List[str]:
        """Detect mentioned sectors in content"""
        detected_sectors = []
        content_lower = content.lower()
        
        for sector, config in self.sector_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    detected_sectors.append(sector)
                    break
        
        return detected_sectors
    
    async def score_sectoral_alignment(self, detected_sectors: List[str]) -> Tuple[float, List[str]]:
        """Score sectoral alignment with development priorities"""
        if not detected_sectors:
            return 0.5, []
        
        # Calculate weighted score based on sector priorities
        sector_scores = []
        priority_flags = []
        
        for sector in detected_sectors:
            config = self.sector_patterns.get(sector, {})
            weight = config.get('weight', 1.0)
            priority = config.get('priority', SectorPriority.MEDIUM)
            
            sector_scores.append(weight)
            
            if priority == SectorPriority.CRITICAL:
                priority_flags.append(f"critical_sector_{sector}")
            elif priority == SectorPriority.HIGH:
                priority_flags.append(f"high_priority_sector_{sector}")
        
        # Calculate average score
        sectoral_score = mean(sector_scores) if sector_scores else 1.0
        
        return sectoral_score, priority_flags
    
    async def check_cross_sectoral_impact(self, content: str) -> Dict[str, Any]:
        """Check for cross-sectoral impact indicators"""
        cross_sectoral_patterns = {
            'health_tech': r'health.*tech|medical.*AI|diagnostic.*algorithm',
            'agri_tech': r'agri.*tech|precision.*agriculture|smart.*farming',
            'climate_tech': r'climate.*tech|green.*tech|clean.*tech',
            'edu_tech': r'edu.*tech|learning.*AI|educational.*platform',
            'fin_health': r'health.*insurance|medical.*payment|health.*savings',
            'agri_climate': r'climate.*smart.*agriculture|sustainable.*farming',
            'multi_sectoral': r'multi.*sector|cross.*sector|integrated.*approach'
        }
        
        detected_combinations = []
        content_lower = content.lower()
        
        for combination, pattern in cross_sectoral_patterns.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                detected_combinations.append(combination)
        
        return {
            'cross_sectoral_indicators': detected_combinations,
            'impact_multiplier': 1.2 if detected_combinations else 1.0
        }

# =============================================================================
# INCLUSION SIGNAL DETECTION
# =============================================================================

class InclusionSignalDetector:
    """Detects signals for gender, youth, and other inclusion priorities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Inclusion detection patterns
        self.inclusion_patterns = {
            InclusionCategory.WOMEN_LED: {
                'patterns': [
                    r'women-led|female-led|women entrepreneurs|women founders',
                    r'gender equality|women in tech|female innovators',
                    r'women empowerment|gender inclusive|female participation',
                    r'mother|maternal|pregnancy|reproductive health',
                    r'gender gap|women\'s economic empowerment'
                ],
                'weight': 1.5
            },
            InclusionCategory.YOUTH_FOCUSED: {
                'patterns': [
                    r'youth|young entrepreneurs|under 35|millennials',
                    r'early career|students|recent graduates|emerging leaders',
                    r'youth innovation|young professionals|next generation',
                    r'student startup|university incubator|campus innovation',
                    r'youth empowerment|young leaders|future leaders'
                ],
                'weight': 1.3
            },
            InclusionCategory.RURAL_PRIORITY: {
                'patterns': [
                    r'rural communities|remote areas|off-grid|countryside',
                    r'last mile|underserved populations|marginalized communities',
                    r'village|township|rural development|agricultural communities',
                    r'digital divide|connectivity gap|rural access',
                    r'smallholder|subsistence|pastoral|nomadic'
                ],
                'weight': 1.4
            },
            InclusionCategory.DISABILITY_INCLUSIVE: {
                'patterns': [
                    r'disability|disabled|accessibility|assistive technology',
                    r'inclusive design|universal design|barrier-free',
                    r'visual impairment|hearing impairment|mobility',
                    r'autism|cognitive|neurological|rehabilitation',
                    r'sign language|braille|screen reader|adaptive'
                ],
                'weight': 1.6
            },
            InclusionCategory.REFUGEE_FOCUSED: {
                'patterns': [
                    r'refugee|displaced|asylum|migration|humanitarian',
                    r'conflict-affected|post-conflict|fragile states',
                    r'emergency response|crisis|disaster|resilience',
                    r'internally displaced|IDP|stateless|vulnerable populations',
                    r'refugee camp|settlement|host communities'
                ],
                'weight': 1.7
            }
        }
    
    async def detect_inclusion_signals(self, content: str) -> List[InclusionCategory]:
        """Detect inclusion signals in content"""
        detected_categories = []
        content_lower = content.lower()
        
        for category, config in self.inclusion_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    detected_categories.append(category)
                    break
        
        return detected_categories
    
    async def score_inclusion_priority(self, detected_categories: List[InclusionCategory]) -> Tuple[float, List[str]]:
        """Score inclusion priority based on detected categories"""
        if not detected_categories:
            return 0.5, []
        
        # Calculate weighted score based on inclusion priorities
        inclusion_scores = []
        priority_flags = []
        
        for category in detected_categories:
            config = self.inclusion_patterns.get(category, {})
            weight = config.get('weight', 1.0)
            
            inclusion_scores.append(weight)
            priority_flags.append(f"inclusion_{category.value}")
        
        # Calculate average score with bonus for multiple categories
        base_score = mean(inclusion_scores) if inclusion_scores else 1.0
        
        # Bonus for multiple inclusion categories
        if len(detected_categories) > 1:
            base_score *= 1.1
        
        return base_score, priority_flags
    
    async def check_diversity_indicators(self, content: str) -> Dict[str, Any]:
        """Check for diversity and inclusion indicators"""
        diversity_patterns = {
            'diverse_team': r'diverse.*team|inclusive.*team|multicultural.*team',
            'minority_focus': r'minority|marginalized|underrepresented',
            'intersectional': r'intersectional|multiple.*identities|complex.*needs',
            'community_driven': r'community.*driven|grassroots|bottom.*up|participatory',
            'local_ownership': r'local.*ownership|community.*ownership|indigenous.*led'
        }
        
        detected_indicators = []
        content_lower = content.lower()
        
        for indicator, pattern in diversity_patterns.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                detected_indicators.append(indicator)
        
        return {
            'diversity_indicators': detected_indicators,
            'inclusion_multiplier': 1.1 if detected_indicators else 1.0
        }

# =============================================================================
# FUNDING STAGE INTELLIGENCE
# =============================================================================

class FundingStageDetector:
    """Intelligent funding stage detection and progression tracking"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Funding stage patterns with amounts and keywords
        self.stage_patterns = {
            'pre_seed': {
                'amounts': (0, 100_000),
                'keywords': [
                    r'idea stage|concept|prototype|MVP|minimum viable product',
                    r'pre-seed|proof of concept|pilot|feasibility',
                    r'ideation|conceptualization|early development',
                    r'research grant|innovation challenge|hackathon'
                ],
                'weight': 1.5  # Higher priority for early stage
            },
            'seed': {
                'amounts': (100_000, 2_000_000),
                'keywords': [
                    r'seed funding|early stage|startup|launch',
                    r'market validation|customer discovery|traction',
                    r'team building|product development|go-to-market',
                    r'angel investor|seed round|initial funding'
                ],
                'weight': 1.3
            },
            'series_a': {
                'amounts': (2_000_000, 15_000_000),
                'keywords': [
                    r'series A|growth|scaling|expansion',
                    r'venture capital|VC|institutional investor',
                    r'market expansion|team scaling|revenue growth',
                    r'established startup|proven model'
                ],
                'weight': 1.0
            },
            'series_b_plus': {
                'amounts': (15_000_000, float('inf')),
                'keywords': [
                    r'series B|series C|later stage|mature',
                    r'international expansion|acquisitions|IPO',
                    r'market leadership|dominant position',
                    r'private equity|growth equity|late stage VC'
                ],
                'weight': 0.8
            },
            'grant': {
                'amounts': (0, 5_000_000),
                'keywords': [
                    r'grant|funding|award|prize|competition',
                    r'research|development|innovation|pilot',
                    r'non-dilutive|equity-free|government|foundation',
                    r'development aid|technical assistance|capacity building'
                ],
                'weight': 1.2
            }
        }
    
    async def detect_funding_stage(self, content: str) -> Optional[str]:
        """Detect funding stage from content"""
        content_lower = content.lower()
        
        # Extract funding amount
        funding_amount = await self._extract_funding_amount(content)
        
        # Check for stage keywords
        stage_scores = {}
        
        for stage, config in self.stage_patterns.items():
            score = 0.0
            
            # Check amount range
            if funding_amount:
                min_amount, max_amount = config['amounts']
                if min_amount <= funding_amount <= max_amount:
                    score += 0.5
            
            # Check keywords
            for keyword_pattern in config['keywords']:
                if re.search(keyword_pattern, content_lower, re.IGNORECASE):
                    score += 0.3
                    break
            
            if score > 0:
                stage_scores[stage] = score * config['weight']
        
        # Return stage with highest score
        if stage_scores:
            return max(stage_scores, key=stage_scores.get)
        
        return None
    
    async def score_stage_priority(self, detected_stage: Optional[str]) -> Tuple[float, List[str]]:
        """Score stage priority based on African funding needs"""
        if not detected_stage:
            return 0.5, []
        
        # Priority scoring based on African funding gap analysis
        stage_priorities = {
            'pre_seed': 1.5,    # Critical gap in early-stage funding
            'seed': 1.3,        # High need for seed funding
            'grant': 1.2,       # Important for research and development
            'series_a': 1.0,    # Standard priority
            'series_b_plus': 0.8 # Lower priority, less critical gap
        }
        
        priority_score = stage_priorities.get(detected_stage, 1.0)
        
        priority_flags = []
        if detected_stage in ['pre_seed', 'seed']:
            priority_flags.append(f"early_stage_{detected_stage}")
        elif detected_stage == 'grant':
            priority_flags.append("non_dilutive_funding")
        
        return priority_score, priority_flags
    
    async def detect_progression_opportunities(self, content: str) -> Dict[str, Any]:
        """Detect opportunities that help organizations progress through stages"""
        progression_patterns = {
            'follow_on_eligible': r'follow.*on|existing.*portfolio|alumni.*eligible',
            'accelerator_program': r'accelerator|incubator|program|bootcamp',
            'mentorship_support': r'mentorship|coaching|advisory|guidance',
            'network_access': r'network|connections|ecosystem|community',
            'capacity_building': r'capacity.*building|skills.*development|training',
            'technical_assistance': r'technical.*assistance|expert.*support|consultancy'
        }
        
        detected_opportunities = []
        content_lower = content.lower()
        
        for opportunity, pattern in progression_patterns.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                detected_opportunities.append(opportunity)
        
        return {
            'progression_opportunities': detected_opportunities,
            'progression_multiplier': 1.1 if detected_opportunities else 1.0
        }
    
    async def _extract_funding_amount(self, content: str) -> Optional[float]:
        """Extract funding amount from content"""
        amount_patterns = [
            r'\$([0-9,]+(?:\.[0-9]+)?)\s*(million|billion|k|thousand)?',
            r'([0-9,]+(?:\.[0-9]+)?)\s*(million|billion|k|thousand)?\s*dollars?',
            r'USD\s*([0-9,]+(?:\.[0-9]+)?)',
            r'€([0-9,]+(?:\.[0-9]+)?)\s*(million|billion|k|thousand)?',
            r'£([0-9,]+(?:\.[0-9]+)?)\s*(million|billion|k|thousand)?'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, content.lower())
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    
                    # Handle multipliers
                    if len(match.groups()) > 1 and match.group(2):
                        multiplier = match.group(2).lower()
                        if multiplier in ['million', 'm']:
                            amount *= 1_000_000
                        elif multiplier in ['billion', 'b']:
                            amount *= 1_000_000_000
                        elif multiplier in ['thousand', 'k']:
                            amount *= 1_000
                    
                    return amount
                except ValueError:
                    continue
        
        return None

# =============================================================================
# EQUITY-AWARE CONTENT CLASSIFIER
# =============================================================================

class EquityAwareContentClassifier:
    """Main equity-aware content classification system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize component detectors
        self.geographic_detector = GeographicBiasDetector()
        self.sectoral_detector = SectoralAlignmentDetector()
        self.inclusion_detector = InclusionSignalDetector()
        self.stage_detector = FundingStageDetector()
        
        # Base content classification patterns
        self.content_type_patterns = {
            'intelligence_item': [
                r'application|apply|deadline|eligibility|criteria',
                r'grant|funding|investment|prize|award|competition',
                r'call for proposals|request for proposals|RFP|CFP',
                r'submit|proposal|application form|guidelines'
            ],
            'funding_announcement': [
                r'announces|announced|receives|received|awarded',
                r'funding.*announcement|investment.*announcement',
                r'press release|news|media|statement',
                r'partnership|collaboration|agreement|deal'
            ],
            'program_description': [
                r'program|initiative|project|platform|service',
                r'launches|launching|introduces|unveils',
                r'overview|description|about|mission|vision'
            ]
        }
    
    async def classify_content(self, content: Dict[str, Any]) -> ClassificationResult:
        """Classify content with equity-aware enhancements"""
        try:
            title = content.get('title', '')
            description = content.get('description', '')
            full_content = f"{title} {description}"
            
            # Base content type classification
            content_type = await self._classify_content_type(full_content)
            base_confidence = await self._calculate_base_confidence(full_content, content_type)
            
            # Geographic analysis
            detected_countries = await self.geographic_detector.detect_countries(full_content)
            geographic_score, geographic_priority = await self.geographic_detector.score_geographic_priority(detected_countries)
            geographic_inclusion = await self.geographic_detector.check_geographic_inclusion(full_content)
            
            # Sectoral analysis
            detected_sectors = await self.sectoral_detector.detect_sectors(full_content)
            sectoral_score, sectoral_flags = await self.sectoral_detector.score_sectoral_alignment(detected_sectors)
            cross_sectoral = await self.sectoral_detector.check_cross_sectoral_impact(full_content)
            
            # Inclusion analysis
            inclusion_categories = await self.inclusion_detector.detect_inclusion_signals(full_content)
            inclusion_score, inclusion_flags = await self.inclusion_detector.score_inclusion_priority(inclusion_categories)
            diversity_indicators = await self.inclusion_detector.check_diversity_indicators(full_content)
            
            # Funding stage analysis
            funding_stage = await self.stage_detector.detect_funding_stage(full_content)
            stage_score, stage_flags = await self.stage_detector.score_stage_priority(funding_stage)
            progression_opportunities = await self.stage_detector.detect_progression_opportunities(full_content)
            
            # Transparency analysis
            transparency_score, transparency_issues = await self._analyze_transparency(full_content)
            
            # Create comprehensive equity score
            equity_score = EquityScore(
                geographic_score=geographic_score,
                sectoral_score=sectoral_score,
                inclusion_score=inclusion_score,
                stage_score=stage_score,
                transparency_score=transparency_score
            )
            
            # Determine overall priority
            overall_score = equity_score.calculate_overall_score()
            if overall_score >= 1.8:
                equity_score.overall_priority = PriorityScore.CRITICAL
            elif overall_score >= 1.4:
                equity_score.overall_priority = PriorityScore.HIGH
            elif overall_score >= 1.1:
                equity_score.overall_priority = PriorityScore.ELEVATED
            else:
                equity_score.overall_priority = PriorityScore.NORMAL
            
            # Compile priority flags
            priority_flags = []
            priority_flags.extend(sectoral_flags)
            priority_flags.extend(inclusion_flags)
            priority_flags.extend(stage_flags)
            priority_flags.extend(geographic_inclusion.get('inclusion_indicators', []))
            priority_flags.extend(diversity_indicators.get('diversity_indicators', []))
            priority_flags.extend(progression_opportunities.get('progression_opportunities', []))
            
            # Adjust confidence based on equity factors
            equity_adjusted_confidence = await self._adjust_confidence_for_equity(
                base_confidence, equity_score, priority_flags
            )
            
            return ClassificationResult(
                content_type=content_type,
                confidence_score=equity_adjusted_confidence,
                equity_score=equity_score,
                priority_flags=priority_flags,
                detected_countries=detected_countries,
                detected_sectors=detected_sectors,
                inclusion_indicators=inclusion_categories,
                funding_stage=funding_stage,
                transparency_issues=transparency_issues
            )
            
        except Exception as e:
            self.logger.error(f"Content classification failed: {e}")
            # Return default classification on error
            return ClassificationResult(
                content_type='unknown',
                confidence_score=0.0,
                equity_score=EquityScore()
            )
    
    async def _classify_content_type(self, content: str) -> str:
        """Classify basic content type"""
        content_lower = content.lower()
        
        # Score each content type
        type_scores = {}
        for content_type, patterns in self.content_type_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    score += 1
            type_scores[content_type] = score
        
        # Return type with highest score
        if type_scores:
            return max(type_scores, key=type_scores.get)
        
        return 'unknown'
    
    async def _calculate_base_confidence(self, content: str, content_type: str) -> float:
        """Calculate base confidence score"""
        content_lower = content.lower()
        
        # Count matching patterns
        patterns = self.content_type_patterns.get(content_type, [])
        matches = sum(1 for pattern in patterns if re.search(pattern, content_lower, re.IGNORECASE))
        
        # Calculate confidence based on matches
        if matches >= 3:
            return 0.9
        elif matches >= 2:
            return 0.7
        elif matches >= 1:
            return 0.5
        else:
            return 0.3
    
    async def _analyze_transparency(self, content: str) -> Tuple[float, List[str]]:
        """Analyze transparency and clarity of opportunity"""
        content_lower = content.lower()
        
        transparency_indicators = {
            'clear_criteria': r'eligibility|criteria|requirements|qualifications',
            'deadline_specified': r'deadline|due date|closing date|submission date',
            'amount_specified': r'\$[0-9,]+|amount|funding|budget|financial',
            'application_process': r'application|submit|proposal|how to apply',
            'contact_information': r'contact|email|phone|website|more information'
        }
        
        present_indicators = []
        for indicator, pattern in transparency_indicators.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                present_indicators.append(indicator)
        
        # Calculate transparency score
        transparency_score = len(present_indicators) / len(transparency_indicators)
        
        # Identify transparency issues
        transparency_issues = []
        if 'clear_criteria' not in present_indicators:
            transparency_issues.append('missing_eligibility_criteria')
        if 'deadline_specified' not in present_indicators:
            transparency_issues.append('missing_deadline')
        if 'amount_specified' not in present_indicators:
            transparency_issues.append('missing_funding_amount')
        if 'application_process' not in present_indicators:
            transparency_issues.append('unclear_application_process')
        
        return transparency_score, transparency_issues
    
    async def _adjust_confidence_for_equity(self, base_confidence: float, equity_score: EquityScore, 
                                          priority_flags: List[str]) -> float:
        """Adjust confidence based on equity factors"""
        # Boost confidence for high-equity opportunities
        equity_multiplier = 1.0
        
        if equity_score.overall_priority == PriorityScore.CRITICAL:
            equity_multiplier = 1.3
        elif equity_score.overall_priority == PriorityScore.HIGH:
            equity_multiplier = 1.2
        elif equity_score.overall_priority == PriorityScore.ELEVATED:
            equity_multiplier = 1.1
        elif equity_score.overall_priority == PriorityScore.LOW:
            equity_multiplier = 0.9
        
        # Additional boosts for specific priorities
        if any('underserved_country' in flag for flag in priority_flags):
            equity_multiplier *= 1.1
        if any('critical_sector' in flag for flag in priority_flags):
            equity_multiplier *= 1.1
        if any('inclusion_' in flag for flag in priority_flags):
            equity_multiplier *= 1.05
        
        # Apply multiplier with reasonable bounds
        adjusted_confidence = base_confidence * equity_multiplier
        return min(1.0, max(0.0, adjusted_confidence))

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_usage():
    """Example usage of equity-aware content classifier"""
    classifier = EquityAwareContentClassifier()
    
    # Test content focusing on underserved regions and priority sectors
    test_content = {
        'title': 'AI for Health Initiative in Central African Republic - $500K Grant',
        'description': 'Healthcare technology grant supporting women-led startups in rural Central African Republic. Focus on maternal health solutions using AI for early diagnosis in remote clinics. Applications due March 2024.',
        'url': 'https://example.org/ai-health-car'
    }
    
    # Classify content
    result = await classifier.classify_content(test_content)
    
    print("=== Equity-Aware Classification Results ===")
    print(f"Content Type: {result.content_type}")
    print(f"Confidence Score: {result.confidence_score:.3f}")
    print(f"Overall Equity Score: {result.equity_score.calculate_overall_score():.3f}")
    print(f"Priority Level: {result.equity_score.overall_priority.value}")
    print(f"Detected Countries: {result.detected_countries}")
    print(f"Detected Sectors: {result.detected_sectors}")
    print(f"Inclusion Indicators: {[cat.value for cat in result.inclusion_indicators]}")
    print(f"Funding Stage: {result.funding_stage}")
    print(f"Priority Flags: {result.priority_flags}")
    print(f"Transparency Issues: {result.transparency_issues}")

if __name__ == "__main__":
    asyncio.run(example_usage())