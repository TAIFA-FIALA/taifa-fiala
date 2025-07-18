"""
Entity Extraction and Relationship Mapping for Funding Intelligence
Based on the Notion note: "Where to go from here? AI-Powered Funding Intelligence Pipeline"
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class EntityType(Enum):
    FUNDER = "funder"
    RECIPIENT = "recipient"
    INTERMEDIARY = "intermediary"
    PROGRAM = "program"
    PERSON = "person"
    LOCATION = "location"
    AMOUNT = "amount"
    ORGANIZATION = "organization"
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    CORPORATE = "corporate"
    NGO = "ngo"
    STARTUP = "startup"


class RelationshipType(Enum):
    FUNDS = "funds"
    PARTNERS_WITH = "partners_with"
    COLLABORATES_WITH = "collaborates_with"
    SPONSORS = "sponsors"
    INVESTS_IN = "invests_in"
    PROVIDES_GRANT_TO = "provides_grant_to"
    ACCELERATES = "accelerates"
    SUPPORTS = "supports"
    ACQUIRES = "acquires"
    MENTORS = "mentors"


@dataclass
class Entity:
    """Represents an entity in the funding ecosystem"""
    name: str
    entity_type: EntityType
    confidence: float
    aliases: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    mention_count: int = 1
    
    def __post_init__(self):
        if isinstance(self.entity_type, str):
            self.entity_type = EntityType(self.entity_type)


@dataclass
class Relationship:
    """Represents a relationship between entities"""
    source_entity: str
    target_entity: str
    relationship_type: RelationshipType
    confidence: float
    context: str = ""
    amount: Optional[str] = None
    date: Optional[datetime] = None
    source_content: str = ""
    
    def __post_init__(self):
        if isinstance(self.relationship_type, str):
            self.relationship_type = RelationshipType(self.relationship_type)


class FundingEntityExtractor:
    """
    Extract and track all entities in the funding ecosystem
    """
    
    def __init__(self):
        self.known_funders = self._load_known_funders()
        self.known_recipients = self._load_known_recipients()
        self.entity_patterns = self._build_entity_patterns()
    
    def _load_known_funders(self) -> List[str]:
        """Load known funding organizations"""
        return [
            "World Bank", "African Development Bank", "Bill & Melinda Gates Foundation",
            "Google", "Microsoft", "Meta", "OpenAI", "Anthropic", "USAID",
            "UK Aid", "European Union", "United Nations", "UNESCO", "UNICEF",
            "Mastercard Foundation", "Ford Foundation", "Rockefeller Foundation",
            "Omidyar Network", "Acumen", "Y Combinator", "Techstars", "500 Startups",
            "Google.org", "Microsoft AI for Good", "Facebook AI Research"
        ]
    
    def _load_known_recipients(self) -> List[str]:
        """Load known recipient types"""
        return [
            "startup", "university", "research institution", "NGO", "government",
            "accelerator", "incubator", "think tank", "foundation"
        ]
    
    def _build_entity_patterns(self) -> Dict[EntityType, List[str]]:
        """Build regex patterns for entity extraction"""
        return {
            EntityType.AMOUNT: [
                r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|billion|thousand|M|B|K)?',
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|billion|thousand|USD|EUR|GBP)',
                r'(?:USD|EUR|GBP|$)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d+(?:\.\d+)?)\s*(?:million|billion|thousand)\s*(?:dollars|USD|EUR)'
            ],
            EntityType.PERSON: [
                r'(?:CEO|CTO|Director|President|Minister|Dr\.|Prof\.|Mr\.|Ms\.)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s+(?:CEO|CTO|Director|President|Minister)',
            ],
            EntityType.LOCATION: [
                r'\b(South Africa|Nigeria|Kenya|Ghana|Rwanda|Uganda|Tanzania|Morocco|Egypt|Ethiopia|Senegal|Ivory Coast|Cameroon|Botswana|Namibia|Zambia|Zimbabwe|Malawi|Mozambique|Madagascar|Mauritius|Seychelles|Cape Verde|Gambia|Guinea|Mali|Burkina Faso|Niger|Chad|Central African Republic|Democratic Republic of Congo|Republic of Congo|Gabon|Equatorial Guinea|Sao Tome and Principe|Comoros|Djibouti|Eritrea|Somalia|Sudan|South Sudan|Libya|Tunisia|Algeria|Benin|Togo|Sierra Leone|Liberia|Guinea-Bissau|Lesotho|Swaziland|Burundi|Angola)\b',
                r'\b(Lagos|Nairobi|Cape Town|Johannesburg|Cairo|Casablanca|Accra|Kigali|Dar es Salaam|Addis Ababa|Tunis|Algiers|Dakar|Abidjan|Kampala|Lusaka|Harare|Maputo|Windhoek|Gaborone|Antananarivo|Port Louis|Praia|Banjul|Conakry|Bamako|Ouagadougou|Niamey|N\'Djamena|Bangui|Kinshasa|Brazzaville|Libreville|Malabo|Sao Tome|Moroni|Mogadishu|Khartoum|Juba|Tripoli|Cotonou|Lome|Freetown|Monrovia|Bissau|Maseru|Mbabane|Bujumbura|Luanda)\b'
            ]
        }
    
    async def extract_entities(self, content: str) -> Dict[str, List[Entity]]:
        """
        Extract funding-related entities from content
        """
        entities = {
            'funders': [],
            'recipients': [],
            'intermediaries': [],
            'amounts': [],
            'programs': [],
            'locations': [],
            'people': [],
            'organizations': []
        }
        
        # Extract using LLM
        llm_entities = await self._llm_entity_extraction(content)
        
        # Extract using patterns
        pattern_entities = self._pattern_entity_extraction(content)
        
        # Merge results
        merged_entities = self._merge_entity_results(llm_entities, pattern_entities)
        
        return merged_entities
    
    async def _llm_entity_extraction(self, content: str) -> Dict[str, List[Entity]]:
        """
        Use LLM for sophisticated entity extraction
        """
        prompt = f"""
        Extract funding-related entities from this text:
        {content}

        Identify:
        1. Funding organizations (even if just mentioned as "partners")
        2. Potential recipient organizations
        3. Program names that might have funding
        4. Any amounts mentioned (even indirect like "multi-million")
        5. Geographic locations at all levels
        6. Key people who might be decision makers
        7. Organizations of any type

        Also infer:
        - If Organization A "partners with" Organization B for AI in Africa,
          who is likely the funder?
        - What type of funding might this lead to?
        - What are the organizational relationships?

        Return structured JSON:
        {{
            "funders": [
                {{"name": "Organization Name", "confidence": 0.9, "type": "corporate|government|foundation|multilateral"}}
            ],
            "recipients": [
                {{"name": "Organization Name", "confidence": 0.8, "type": "startup|university|ngo|government"}}
            ],
            "programs": [
                {{"name": "Program Name", "confidence": 0.7, "description": "Brief description"}}
            ],
            "amounts": [
                {{"amount": "$10 million", "confidence": 0.9, "context": "where it was mentioned"}}
            ],
            "locations": [
                {{"location": "Country/City", "confidence": 0.9, "level": "country|city|region"}}
            ],
            "people": [
                {{"name": "Person Name", "confidence": 0.8, "role": "CEO|Director|Minister", "organization": "Org Name"}}
            ],
            "organizations": [
                {{"name": "Organization Name", "confidence": 0.9, "type": "corporate|government|ngo|academic|startup"}}
            ]
        }}
        """
        
        # TODO: Integrate with your LLM service
        # For now, return mock response
        return await self._mock_llm_entities(content)
    
    def _pattern_entity_extraction(self, content: str) -> Dict[str, List[Entity]]:
        """
        Extract entities using regex patterns
        """
        entities = {
            'amounts': [],
            'locations': [],
            'people': [],
            'organizations': []
        }
        
        # Extract amounts
        for pattern in self.entity_patterns[EntityType.AMOUNT]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                entities['amounts'].append(Entity(
                    name=match,
                    entity_type=EntityType.AMOUNT,
                    confidence=0.9
                ))
        
        # Extract locations
        for pattern in self.entity_patterns[EntityType.LOCATION]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                entities['locations'].append(Entity(
                    name=match,
                    entity_type=EntityType.LOCATION,
                    confidence=0.8
                ))
        
        # Extract people
        for pattern in self.entity_patterns[EntityType.PERSON]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                entities['people'].append(Entity(
                    name=match,
                    entity_type=EntityType.PERSON,
                    confidence=0.7
                ))
        
        # Extract known funders
        for funder in self.known_funders:
            if funder.lower() in content.lower():
                entities['organizations'].append(Entity(
                    name=funder,
                    entity_type=EntityType.FUNDER,
                    confidence=0.9
                ))
        
        return entities
    
    def _merge_entity_results(self, llm_entities: Dict[str, List[Entity]], 
                            pattern_entities: Dict[str, List[Entity]]) -> Dict[str, List[Entity]]:
        """
        Merge entities from different extraction methods
        """
        merged = {}
        
        # Combine all entity types
        all_keys = set(llm_entities.keys()) | set(pattern_entities.keys())
        
        for key in all_keys:
            merged[key] = []
            
            # Add LLM entities
            if key in llm_entities:
                merged[key].extend(llm_entities[key])
            
            # Add pattern entities
            if key in pattern_entities:
                merged[key].extend(pattern_entities[key])
            
            # Remove duplicates
            merged[key] = self._deduplicate_entities(merged[key])
        
        return merged
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Remove duplicate entities
        """
        seen = set()
        deduplicated = []
        
        for entity in entities:
            key = (entity.name.lower(), entity.entity_type)
            if key not in seen:
                seen.add(key)
                deduplicated.append(entity)
        
        return deduplicated
    
    async def _mock_llm_entities(self, content: str) -> Dict[str, List[Entity]]:
        """
        Mock LLM response for development
        """
        entities = {
            'funders': [],
            'recipients': [],
            'programs': [],
            'amounts': [],
            'locations': [],
            'people': [],
            'organizations': []
        }
        
        # Simple mock extraction
        if "google" in content.lower():
            entities['funders'].append(Entity("Google", EntityType.FUNDER, 0.9))
        if "microsoft" in content.lower():
            entities['funders'].append(Entity("Microsoft", EntityType.FUNDER, 0.9))
        if "africa" in content.lower():
            entities['locations'].append(Entity("Africa", EntityType.LOCATION, 0.8))
        
        return entities


class FundingRelationshipMapper:
    """
    Build a knowledge graph of funding relationships
    """
    
    def __init__(self):
        self.relationship_patterns = self._build_relationship_patterns()
    
    def _build_relationship_patterns(self) -> Dict[RelationshipType, List[str]]:
        """
        Build patterns for relationship extraction
        """
        return {
            RelationshipType.FUNDS: [
                r'(\w+(?:\s+\w+)*)\s+(?:funds|funded|financing|granted)\s+(\w+(?:\s+\w+)*)',
                r'(\w+(?:\s+\w+)*)\s+(?:provided|gives|gave)\s+(?:funding|grant|investment)\s+to\s+(\w+(?:\s+\w+)*)',
            ],
            RelationshipType.PARTNERS_WITH: [
                r'(\w+(?:\s+\w+)*)\s+(?:partners|partnered|partnership)\s+with\s+(\w+(?:\s+\w+)*)',
                r'(\w+(?:\s+\w+)*)\s+(?:and|&)\s+(\w+(?:\s+\w+)*)\s+(?:announced|signed|formed)\s+(?:partnership|alliance)',
            ],
            RelationshipType.INVESTS_IN: [
                r'(\w+(?:\s+\w+)*)\s+(?:invests|invested|investment)\s+in\s+(\w+(?:\s+\w+)*)',
                r'(\w+(?:\s+\w+)*)\s+(?:led|leads|leading)\s+(?:investment|round|funding)\s+in\s+(\w+(?:\s+\w+)*)',
            ],
            RelationshipType.SPONSORS: [
                r'(\w+(?:\s+\w+)*)\s+(?:sponsors|sponsored|sponsoring)\s+(\w+(?:\s+\w+)*)',
                r'(\w+(?:\s+\w+)*)\s+(?:is|was)\s+(?:sponsored|supported)\s+by\s+(\w+(?:\s+\w+)*)',
            ]
        }
    
    async def map_relationships(self, entities: Dict[str, List[Entity]], 
                              content: str) -> List[Relationship]:
        """
        Create relationships between entities
        """
        relationships = []
        
        # Extract relationships using patterns
        pattern_relationships = self._pattern_relationship_extraction(content)
        relationships.extend(pattern_relationships)
        
        # Infer relationships from entity co-occurrence
        inferred_relationships = self._infer_relationships_from_entities(entities, content)
        relationships.extend(inferred_relationships)
        
        # Use LLM for sophisticated relationship extraction
        llm_relationships = await self._llm_relationship_extraction(entities, content)
        relationships.extend(llm_relationships)
        
        return relationships
    
    def _pattern_relationship_extraction(self, content: str) -> List[Relationship]:
        """
        Extract relationships using regex patterns
        """
        relationships = []
        
        for rel_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        relationships.append(Relationship(
                            source_entity=match[0],
                            target_entity=match[1],
                            relationship_type=rel_type,
                            confidence=0.7,
                            context=content[:200],  # First 200 chars for context
                            source_content=content
                        ))
        
        return relationships
    
    def _infer_relationships_from_entities(self, entities: Dict[str, List[Entity]], 
                                         content: str) -> List[Relationship]:
        """
        Infer relationships based on entity co-occurrence
        """
        relationships = []
        
        # If funders and recipients appear together, likely funding relationship
        for funder in entities.get('funders', []):
            for recipient in entities.get('recipients', []):
                if funder.name.lower() in content.lower() and recipient.name.lower() in content.lower():
                    relationships.append(Relationship(
                        source_entity=funder.name,
                        target_entity=recipient.name,
                        relationship_type=RelationshipType.FUNDS,
                        confidence=0.6,
                        context="Inferred from co-occurrence",
                        source_content=content
                    ))
        
        return relationships
    
    async def _llm_relationship_extraction(self, entities: Dict[str, List[Entity]], 
                                         content: str) -> List[Relationship]:
        """
        Use LLM to extract sophisticated relationships
        """
        # TODO: Implement LLM relationship extraction
        return []
    
    def calculate_relationship_confidence(self, source: str, target: str, 
                                        content: str) -> float:
        """
        Calculate confidence score for a relationship
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on explicit relationship words
        relationship_words = ['funds', 'invests', 'partners', 'sponsors', 'collaborates']
        for word in relationship_words:
            if word in content.lower():
                confidence += 0.1
        
        # Increase confidence based on amounts mentioned
        if any(char.isdigit() for char in content):
            confidence += 0.1
        
        # Increase confidence based on formal language
        formal_words = ['announces', 'agreement', 'contract', 'MOU', 'partnership']
        for word in formal_words:
            if word in content.lower():
                confidence += 0.1
        
        return min(confidence, 1.0)


class FundingTimelineBuilder:
    """
    Track funding events over time to identify patterns
    """
    
    def __init__(self):
        self.event_history = []
    
    async def build_timeline(self, organization: str, 
                           content_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build timeline for an organization
        """
        timeline = []
        
        for content in content_history:
            if organization.lower() in content.get('text', '').lower():
                timeline.append({
                    'date': content.get('date', datetime.now()),
                    'type': content.get('event_type', 'unknown'),
                    'description': content.get('text', '')[:200],
                    'funding_implications': content.get('funding_implications', {}),
                    'source': content.get('source', 'unknown')
                })
        
        # Sort by date
        timeline.sort(key=lambda x: x['date'])
        
        # Identify patterns
        patterns = self._identify_patterns(timeline)
        
        # Predict next event
        next_event = self._predict_next_event(patterns, timeline)
        
        return {
            'organization': organization,
            'timeline': timeline,
            'patterns': patterns,
            'next_likely_event': next_event,
            'total_events': len(timeline)
        }
    
    def _identify_patterns(self, timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify funding patterns in timeline
        """
        patterns = []
        
        # Look for partnership → funding patterns
        for i in range(len(timeline) - 1):
            current_event = timeline[i]
            next_event = timeline[i + 1]
            
            if ('partnership' in current_event['description'].lower() and 
                'funding' in next_event['description'].lower()):
                
                days_between = (next_event['date'] - current_event['date']).days
                patterns.append({
                    'pattern': 'partnership_to_funding',
                    'typical_delay': days_between,
                    'confidence': 0.8,
                    'description': f"Partnership announcements typically lead to funding after {days_between} days"
                })
        
        return patterns
    
    def _predict_next_event(self, patterns: List[Dict[str, Any]], 
                          timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict the next likely event based on patterns
        """
        if not timeline:
            return {'prediction': 'No timeline data available', 'confidence': 0.0}
        
        last_event = timeline[-1]
        
        # Look for matching patterns
        for pattern in patterns:
            if pattern['pattern'] == 'partnership_to_funding':
                predicted_date = last_event['date'] + timedelta(days=pattern['typical_delay'])
                return {
                    'prediction': 'Funding announcement likely',
                    'predicted_date': predicted_date,
                    'confidence': pattern['confidence'],
                    'rationale': f"Based on {pattern['pattern']} pattern"
                }
        
        # Default prediction
        return {
            'prediction': 'Continue monitoring for announcements',
            'confidence': 0.3,
            'rationale': 'Insufficient pattern data'
        }