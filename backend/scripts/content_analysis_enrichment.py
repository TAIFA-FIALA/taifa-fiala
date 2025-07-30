#!/usr/bin/env python3
"""
Content Analysis Enrichment Script
Analyzes existing title/description content to extract missing metadata fields:
- organization, deadline, country, region, sector
- amount_min, amount_max, funding_type
Uses Supabase client (RLS-compatible) and AI/NLP techniques.
"""

import asyncio
import json
import os
import re
import sys
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import dateutil.parser

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from supabase import create_client, Client

class ContentAnalysisEnricher:
    def __init__(self):
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL", "https://turcbnsgdlyelzmcqixd.supabase.co")
        supabase_key = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1cmNibnNnZGx5ZWx6bWNxaXhkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjY1NzQ4OCwiZXhwIjoyMDY4MjMzNDg4fQ.Vdn2zHMhQ2V6rJf-MazNX1wxXJknnYighekkruEXMrA")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Analysis stats
        self.stats = {
            'total_analyzed': 0,
            'organizations_extracted': 0,
            'deadlines_extracted': 0,
            'countries_extracted': 0,
            'sectors_extracted': 0,
            'amounts_extracted': 0,
            'quality_scores': []
        }
        
        # Known patterns and mappings
        self._setup_extraction_patterns()
        
        print(f"✅ Content Analysis Enricher initialized (Supabase RLS-compatible)")
    
    def _setup_extraction_patterns(self):
        """Set up regex patterns and mappings for content extraction"""
        
        # Organization patterns
        self.org_patterns = [
            r'(?:by|from|funded by|sponsored by|organized by)\s+([A-Z][A-Za-z\s&]+(?:Foundation|Fund|Agency|Organization|Institute|University|Bank|Group|Initiative|Program|Council|Commission|Development))',
            r'([A-Z][A-Za-z\s&]+(?:Foundation|Fund|Agency|Organization|Institute|University|Bank|Group|Initiative|Program|Council|Commission|Development))\s+(?:announces|launches|offers|provides)',
            r'The\s+([A-Z][A-Za-z\s&]+(?:Foundation|Fund|Agency|Organization|Institute|University|Bank|Group|Initiative|Program|Council|Commission|Development))',
        ]
        
        # Deadline patterns
        self.deadline_patterns = [
            r'(?:deadline|due|closes?|ends?|expires?|applications?\s+close)\s*:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'(?:deadline|due|closes?|ends?|expires?)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:by|before|until)\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'(\d{4}-\d{2}-\d{2})',  # ISO format
        ]
        
        # Amount patterns
        self.amount_patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|M)\b',  # $5 million
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:thousand|K)\b',  # $500 thousand
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b',  # $50,000
            r'(?:up to|maximum of|max)\s*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:USD|dollars?)',
        ]
        
        # Country/region mappings
        self.african_countries = {
            'nigeria', 'kenya', 'south africa', 'ghana', 'uganda', 'tanzania', 'ethiopia',
            'morocco', 'egypt', 'algeria', 'tunisia', 'rwanda', 'senegal', 'ivory coast',
            'cameroon', 'zambia', 'zimbabwe', 'botswana', 'namibia', 'mali', 'burkina faso',
            'madagascar', 'mozambique', 'angola', 'democratic republic of congo', 'congo',
            'gabon', 'chad', 'niger', 'mauritania', 'libya', 'sudan', 'somalia', 'eritrea',
            'djibouti', 'gambia', 'guinea', 'sierra leone', 'liberia', 'togo', 'benin',
            'central african republic', 'equatorial guinea', 'sao tome and principe',
            'cape verde', 'comoros', 'mauritius', 'seychelles', 'lesotho', 'swaziland'
        }
        
        # AI/Tech sector keywords
        self.ai_sectors = {
            'artificial intelligence': 'AI/ML',
            'machine learning': 'AI/ML', 
            'deep learning': 'AI/ML',
            'natural language processing': 'NLP',
            'computer vision': 'Computer Vision',
            'robotics': 'Robotics',
            'fintech': 'FinTech',
            'healthtech': 'HealthTech',
            'agtech': 'AgTech',
            'edtech': 'EdTech',
            'blockchain': 'Blockchain',
            'data science': 'Data Science',
            'cybersecurity': 'Cybersecurity',
            'iot': 'IoT',
            'internet of things': 'IoT'
        }
    
    def analyze_content_quality(self, title: str, description: str) -> Dict[str, Any]:
        """Analyze the quality and extractability of content"""
        
        quality_score = 0
        indicators = {
            'has_structured_info': False,
            'has_dates': False,
            'has_amounts': False,
            'has_organizations': False,
            'has_locations': False,
            'content_length': len(description) if description else 0
        }
        
        combined_text = f"{title} {description}".lower() if description else title.lower()
        
        # Check for structured information
        if any(pattern in combined_text for pattern in ['deadline:', 'amount:', 'eligibility:', 'requirements:']):
            indicators['has_structured_info'] = True
            quality_score += 20
        
        # Check for dates
        if re.search(r'\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|january|february|march|april|may|june|july|august|september|october|november|december', combined_text):
            indicators['has_dates'] = True
            quality_score += 15
        
        # Check for amounts
        if re.search(r'\$|usd|dollars?|million|thousand|funding|grant', combined_text):
            indicators['has_amounts'] = True
            quality_score += 15
        
        # Check for organizations
        if re.search(r'foundation|fund|agency|organization|institute|university|bank|group|initiative|program', combined_text):
            indicators['has_organizations'] = True
            quality_score += 20
        
        # Check for locations
        if any(country in combined_text for country in self.african_countries):
            indicators['has_locations'] = True
            quality_score += 15
        
        # Content length bonus
        if indicators['content_length'] > 200:
            quality_score += 10
        elif indicators['content_length'] > 100:
            quality_score += 5
        
        return {
            'quality_score': min(quality_score, 100),
            'indicators': indicators
        }
    
    def extract_organization(self, title: str, description: str) -> Optional[str]:
        """Extract organization name from content"""
        
        combined_text = f"{title} {description}" if description else title
        
        for pattern in self.org_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                org = match.group(1).strip()
                # Clean up common artifacts
                org = re.sub(r'\s+', ' ', org)
                if len(org) > 5 and len(org) < 100:  # Reasonable length
                    return org
        
        return None
    
    def extract_deadline(self, title: str, description: str) -> Optional[str]:
        """Extract deadline from content"""
        
        combined_text = f"{title} {description}" if description else title
        
        for pattern in self.deadline_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                try:
                    # Try to parse and standardize the date
                    parsed_date = dateutil.parser.parse(date_str, fuzzy=True)
                    # Only return future dates or dates within last 6 months
                    if parsed_date.date() >= (datetime.now() - timedelta(days=180)).date():
                        return parsed_date.strftime('%Y-%m-%d')
                except:
                    continue
        
        return None
    
    def extract_country_region(self, title: str, description: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract country and region from content"""
        
        combined_text = f"{title} {description}".lower() if description else title.lower()
        
        # Look for African countries
        for country in self.african_countries:
            if country in combined_text:
                # Determine region based on country
                region = self._get_african_region(country)
                return country.title(), region
        
        # Look for regional terms
        if 'west africa' in combined_text:
            return None, 'West Africa'
        elif 'east africa' in combined_text:
            return None, 'East Africa'
        elif 'north africa' in combined_text:
            return None, 'North Africa'
        elif 'southern africa' in combined_text:
            return None, 'Southern Africa'
        elif 'central africa' in combined_text:
            return None, 'Central Africa'
        elif 'africa' in combined_text:
            return None, 'Africa'
        
        return None, None
    
    def _get_african_region(self, country: str) -> str:
        """Map country to African region"""
        
        west_africa = ['nigeria', 'ghana', 'senegal', 'ivory coast', 'mali', 'burkina faso', 'niger', 'guinea', 'sierra leone', 'liberia', 'togo', 'benin', 'gambia', 'mauritania', 'cape verde']
        east_africa = ['kenya', 'uganda', 'tanzania', 'ethiopia', 'rwanda', 'somalia', 'eritrea', 'djibouti']
        north_africa = ['morocco', 'egypt', 'algeria', 'tunisia', 'libya', 'sudan']
        southern_africa = ['south africa', 'botswana', 'namibia', 'zambia', 'zimbabwe', 'lesotho', 'swaziland', 'mauritius', 'seychelles']
        central_africa = ['democratic republic of congo', 'congo', 'cameroon', 'gabon', 'chad', 'central african republic', 'equatorial guinea', 'sao tome and principe']
        
        if country in west_africa:
            return 'West Africa'
        elif country in east_africa:
            return 'East Africa'
        elif country in north_africa:
            return 'North Africa'
        elif country in southern_africa:
            return 'Southern Africa'
        elif country in central_africa:
            return 'Central Africa'
        else:
            return 'Africa'
    
    def extract_sector(self, title: str, description: str) -> Optional[str]:
        """Extract AI/tech sector from content"""
        
        combined_text = f"{title} {description}".lower() if description else title.lower()
        
        for keyword, sector in self.ai_sectors.items():
            if keyword in combined_text:
                return sector
        
        # Fallback to general categories
        if any(term in combined_text for term in ['health', 'medical', 'healthcare']):
            return 'HealthTech'
        elif any(term in combined_text for term in ['agriculture', 'farming', 'food']):
            return 'AgTech'
        elif any(term in combined_text for term in ['education', 'learning', 'school']):
            return 'EdTech'
        elif any(term in combined_text for term in ['finance', 'banking', 'payment']):
            return 'FinTech'
        elif any(term in combined_text for term in ['technology', 'tech', 'innovation']):
            return 'Technology'
        
        return None
    
    def extract_funding_amounts(self, title: str, description: str) -> Tuple[Optional[float], Optional[float]]:
        """Extract funding amounts from content"""
        
        combined_text = f"{title} {description}" if description else title
        amounts = []
        
        for pattern in self.amount_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            for match in matches:
                try:
                    # Clean and convert amount
                    amount_str = match.replace(',', '')
                    amount = float(amount_str)
                    
                    # Handle scale indicators
                    if 'million' in combined_text.lower() or 'M' in combined_text:
                        amount *= 1000000
                    elif 'thousand' in combined_text.lower() or 'K' in combined_text:
                        amount *= 1000
                    
                    amounts.append(amount)
                except:
                    continue
        
        if amounts:
            amounts.sort()
            min_amount = amounts[0]
            max_amount = amounts[-1] if len(amounts) > 1 else amounts[0]
            return min_amount, max_amount
        
        return None, None
    
    def enrich_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a single record with extracted metadata"""
        
        title = record.get('title', '')
        description = record.get('description', '')
        
        if not title and not description:
            return record
        
        # Analyze content quality
        quality_analysis = self.analyze_content_quality(title, description)
        
        enriched = record.copy()
        extracted_fields = {}
        
        # Extract organization (map to provider_organization_id or add as metadata)
        if not record.get('provider_organization_id'):
            org = self.extract_organization(title, description)
            if org:
                enriched['_extracted_organization'] = org  # Store as metadata for now
                extracted_fields['organization'] = org
                self.stats['organizations_extracted'] += 1
        
        # Extract deadline (map to application_deadline)
        if not record.get('application_deadline'):
            deadline = self.extract_deadline(title, description)
            if deadline:
                enriched['application_deadline'] = deadline
                extracted_fields['application_deadline'] = deadline
                self.stats['deadlines_extracted'] += 1
        
        # Extract country and region (map to geographic_focus)
        if not record.get('geographic_focus'):
            country, region = self.extract_country_region(title, description)
            if country or region:
                geographic_focus = country if country else region
                enriched['geographic_focus'] = geographic_focus
                extracted_fields['geographic_focus'] = geographic_focus
                self.stats['countries_extracted'] += 1
        
        # Extract sector (map to sector_tags)
        if not record.get('sector_tags'):
            sector = self.extract_sector(title, description)
            if sector:
                enriched['sector_tags'] = sector
                extracted_fields['sector_tags'] = sector
                self.stats['sectors_extracted'] += 1
        
        # Extract funding amounts
        if not record.get('amount_min') and not record.get('amount_max'):
            min_amount, max_amount = self.extract_funding_amounts(title, description)
            if min_amount:
                enriched['amount_min'] = min_amount
                extracted_fields['amount_min'] = min_amount
                if max_amount and max_amount != min_amount:
                    enriched['amount_max'] = max_amount
                    extracted_fields['amount_max'] = max_amount
                self.stats['amounts_extracted'] += 1
        
        # Add quality score and extraction metadata
        enriched['_content_quality_score'] = quality_analysis['quality_score']
        enriched['_extracted_fields'] = extracted_fields
        
        self.stats['quality_scores'].append(quality_analysis['quality_score'])
        self.stats['total_analyzed'] += 1
        
        return enriched
    
    def analyze_sample_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Analyze a sample of records to demonstrate content analysis"""
        
        print(f"🔍 Analyzing content quality for {limit} sample records...")
        
        try:
            # Fetch sample records with correct column names
            response = self.supabase.table('africa_intelligence_feed')\
                .select('id, title, description, application_deadline, geographic_focus, sector_tags, amount_min, amount_max, provider_organization_id, funding_type, currency')\
                .limit(limit)\
                .execute()
            
            records = response.data
            
            if not records:
                print("❌ No records found")
                return []
            
            print(f"📊 Processing {len(records)} records...")
            
            # Enrich each record
            enriched_records = []
            for record in records:
                enriched = self.enrich_record(record)
                enriched_records.append(enriched)
            
            return enriched_records
            
        except Exception as e:
            print(f"❌ Error analyzing records: {e}")
            return []
    
    def print_analysis_results(self, enriched_records: List[Dict[str, Any]]):
        """Print analysis results and statistics"""
        
        print("\n" + "="*80)
        print("🧠 CONTENT ANALYSIS ENRICHMENT RESULTS")
        print("="*80)
        
        print(f"📊 EXTRACTION STATISTICS:")
        print(f"  • Total records analyzed: {self.stats['total_analyzed']}")
        print(f"  • Organizations extracted: {self.stats['organizations_extracted']}")
        print(f"  • Deadlines extracted: {self.stats['deadlines_extracted']}")
        print(f"  • Countries extracted: {self.stats['countries_extracted']}")
        print(f"  • Sectors extracted: {self.stats['sectors_extracted']}")
        print(f"  • Funding amounts extracted: {self.stats['amounts_extracted']}")
        
        if self.stats['quality_scores']:
            avg_quality = sum(self.stats['quality_scores']) / len(self.stats['quality_scores'])
            print(f"  • Average content quality score: {avg_quality:.1f}/100")
        
        print(f"\n📝 SAMPLE EXTRACTIONS:")
        
        # Show examples of successful extractions
        examples_shown = 0
        for record in enriched_records:
            if record.get('_extracted_fields') and examples_shown < 5:
                print(f"\n  📄 Record ID: {record.get('id')}")
                print(f"     Title: {record.get('title', '')[:80]}...")
                print(f"     Quality Score: {record.get('_content_quality_score', 0)}/100")
                
                extracted = record.get('_extracted_fields', {})
                if extracted:
                    print(f"     Extracted:")
                    for field, value in extracted.items():
                        print(f"       • {field}: {value}")
                
                examples_shown += 1
        
        print(f"\n🎯 ENRICHMENT RECOMMENDATIONS:")
        
        if self.stats['organizations_extracted'] > 0:
            print(f"  ✅ Organization extraction working well ({self.stats['organizations_extracted']} found)")
        else:
            print(f"  ⚠️ Organization extraction needs improvement")
        
        if self.stats['deadlines_extracted'] > 0:
            print(f"  ✅ Deadline extraction working ({self.stats['deadlines_extracted']} found)")
        else:
            print(f"  ⚠️ Deadline extraction needs better patterns")
        
        if self.stats['countries_extracted'] > 0:
            print(f"  ✅ Geographic extraction working ({self.stats['countries_extracted']} found)")
        else:
            print(f"  ⚠️ Geographic extraction needs improvement")
        
        if self.stats['amounts_extracted'] > 0:
            print(f"  ✅ Funding amount extraction working ({self.stats['amounts_extracted']} found)")
        else:
            print(f"  ⚠️ Funding amount extraction needs better patterns")

def main():
    try:
        enricher = ContentAnalysisEnricher()
        
        # Analyze sample records
        enriched_records = enricher.analyze_sample_records(limit=50)
        
        if enriched_records:
            # Print results
            enricher.print_analysis_results(enriched_records)
            
            # Save results
            output_file = 'content_analysis_results.json'
            with open(output_file, 'w') as f:
                json.dump({
                    'stats': enricher.stats,
                    'sample_records': enriched_records[:10]  # Save first 10 as examples
                }, f, indent=2, default=str)
            
            print(f"\n💾 Results saved to: {output_file}")
            print(f"✅ Content analysis completed successfully!")
            
        else:
            print("❌ Content analysis failed")
            
    except Exception as e:
        print(f"❌ Script failed: {e}")

if __name__ == "__main__":
    main()
