#!/usr/bin/env python3
"""
Data Field Population Analysis Script - Supabase RLS Compatible
Analyzes which fields in the africa_intelligence_feed table are well-populated vs sparse
Uses Supabase client instead of direct database connections (required for RLS).
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, List
from collections import defaultdict

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import Supabase client (RLS-compatible)
from supabase import create_client, Client

class SupabaseFieldAnalyzer:
    def __init__(self):
        # Get Supabase credentials from environment
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        print(f"✅ Connected to Supabase (RLS-compatible)")
        
    def analyze_field_population(self, limit: int = 500) -> Dict[str, Any]:
        """Analyze field population using Supabase client (RLS-compatible)"""
        
        print(f"🔍 Analyzing field population for up to {limit} records...")
        
        try:
            # Use Supabase client to fetch data (respects RLS)
            response = self.supabase.table('africa_intelligence_feed')\
                .select('*')\
                .limit(limit)\
                .execute()
            
            records = response.data
            total_records = len(records)
            
            if total_records == 0:
                print("❌ No records found or no access due to RLS policies")
                return {}
                
            print(f"📊 Successfully fetched {total_records} records via Supabase client")
            
        except Exception as e:
            print(f"❌ Error fetching data via Supabase client: {e}")
            return {}
        
        # Define field categories based on schema analysis
        core_fields = [
            'id', 'title', 'description', 'organization', 'source_url', 
            'application_url', 'deadline', 'country', 'region', 'sector'
        ]
        
        financial_fields = [
            'amount_min', 'amount_max', 'amount_exact', 'currency',
            'funding_type_id', 'total_funding_pool'
        ]
        
        enhanced_fields = [
            'status', 'tags', 'application_tips', 'eligibility_criteria', 
            'application_process', 'selection_criteria', 'project_duration',
            'reporting_requirements', 'target_audience', 'ai_subsectors',
            'development_stage', 'collaboration_required', 'gender_focused',
            'youth_focused', 'community_rating', 'view_count', 'application_count'
        ]
        
        all_fields = core_fields + financial_fields + enhanced_fields
        
        # Analyze each field
        field_stats = {}
        
        for field in all_fields:
            populated_count = 0
            meaningful_count = 0
            sample_values = []
            
            for record in records:
                value = record.get(field)
                
                if value is not None:
                    populated_count += 1
                    
                    if self._is_meaningful_value(value):
                        meaningful_count += 1
                        
                        if len(sample_values) < 3:
                            sample_values.append(str(value)[:80])
            
            population_rate = (populated_count / total_records) * 100
            meaningful_rate = (meaningful_count / total_records) * 100
            
            # Categorize field type
            if field in core_fields:
                category = 'core'
            elif field in financial_fields:
                category = 'financial'
            else:
                category = 'enhanced'
            
            field_stats[field] = {
                'populated_count': populated_count,
                'meaningful_count': meaningful_count,
                'total_records': total_records,
                'population_rate': round(population_rate, 1),
                'meaningful_rate': round(meaningful_rate, 1),
                'sample_values': sample_values,
                'category': category
            }
        
        # Categorize by data quality
        excellent = {}      # >80% meaningful
        good = {}          # 50-80% meaningful  
        moderate = {}      # 20-50% meaningful
        poor = {}          # <20% meaningful
        
        for field, stats in field_stats.items():
            rate = stats['meaningful_rate']
            
            if rate >= 80:
                excellent[field] = stats
            elif rate >= 50:
                good[field] = stats
            elif rate >= 20:
                moderate[field] = stats
            else:
                poor[field] = stats
        
        analysis = {
            'total_records_analyzed': total_records,
            'connection_method': 'supabase_client_rls_compatible',
            'field_stats': field_stats,
            'excellent_fields': excellent,
            'good_fields': good,
            'moderate_fields': moderate,
            'poor_fields': poor,
            'ui_recommendations': self._generate_ui_recommendations(excellent, good, moderate, poor),
            'backend_priorities': self._generate_backend_priorities(excellent, good, moderate, poor)
        }
        
        return analysis
    
    def _is_meaningful_value(self, value) -> bool:
        """Check if a value contains meaningful content"""
        if value is None:
            return False
        
        if isinstance(value, str):
            # Clean and check string content
            cleaned = value.strip().lower()
            if not cleaned:
                return False
            if len(cleaned) < 2:
                return False
            # Common placeholder/empty values
            if cleaned in ['n/a', 'na', 'null', 'none', 'tbd', 'unknown', '', 'undefined', 'null']:
                return False
        
        if isinstance(value, (list, dict)):
            return len(value) > 0
        
        if isinstance(value, (int, float)):
            return value > 0
        
        if isinstance(value, bool):
            return True  # Boolean values are always meaningful
        
        return True
    
    def _generate_ui_recommendations(self, excellent, good, moderate, poor) -> List[str]:
        """Generate UI improvement recommendations"""
        recommendations = []
        
        # Fields to display prominently
        prominent_fields = list(excellent.keys()) + list(good.keys())
        recommendations.append(f"Display prominently: {', '.join(prominent_fields[:10])}")
        
        # Fields to display conditionally
        conditional_fields = list(moderate.keys())
        if conditional_fields:
            recommendations.append(f"Display conditionally: {', '.join(conditional_fields[:8])}")
        
        # Fields to hide/minimize
        hidden_fields = list(poor.keys())
        if hidden_fields:
            recommendations.append(f"Hide when empty: {', '.join(hidden_fields[:8])}")
        
        # Specific UI recommendations
        if 'deadline' in excellent:
            recommendations.append("✅ Deadline data is excellent - keep prominent with urgency indicators")
        elif 'deadline' in poor:
            recommendations.append("⚠️ Deadline data is poor - show 'Rolling applications' fallback")
        
        if any(field in poor for field in ['amount_min', 'amount_max', 'amount_exact']):
            recommendations.append("💰 Funding amounts are sparse - use 'Amount varies' fallbacks")
        
        if 'tags' in poor:
            recommendations.append("🏷️ Tags are sparse - hide tag section when empty")
        
        return recommendations
    
    def _generate_backend_priorities(self, excellent, good, moderate, poor) -> List[str]:
        """Generate backend enrichment priorities"""
        priorities = []
        
        # High priority: Core fields that are poor
        core_poor = [f for f in poor.keys() if poor[f]['category'] == 'core']
        if core_poor:
            priorities.append(f"🚨 HIGH PRIORITY - Fix core fields: {', '.join(core_poor)}")
        
        # Medium priority: Financial fields that are poor/moderate
        financial_issues = [f for f in list(poor.keys()) + list(moderate.keys()) 
                          if f in ['amount_min', 'amount_max', 'currency', 'funding_type_id']]
        if financial_issues:
            priorities.append(f"💰 MEDIUM PRIORITY - Improve financial data: {', '.join(financial_issues)}")
        
        # Low priority: Enhanced fields
        enhanced_poor = [f for f in poor.keys() if poor[f]['category'] == 'enhanced']
        if enhanced_poor:
            priorities.append(f"📈 LOW PRIORITY - Enhance optional fields: {', '.join(enhanced_poor[:5])}")
        
        return priorities
    
    def print_analysis(self, analysis: Dict[str, Any]):
        """Print comprehensive analysis results"""
        
        print("\n" + "="*80)
        print("📊 SUPABASE RLS-COMPATIBLE FIELD ANALYSIS")
        print("="*80)
        
        print(f"📈 Total Records: {analysis['total_records_analyzed']}")
        print(f"🔗 Connection: {analysis['connection_method']}")
        
        print(f"\n🌟 EXCELLENT FIELDS (≥80% meaningful):")
        for field, stats in analysis['excellent_fields'].items():
            print(f"  ✅ {field}: {stats['meaningful_rate']}% ({stats['category']})")
        
        print(f"\n👍 GOOD FIELDS (50-80% meaningful):")
        for field, stats in analysis['good_fields'].items():
            print(f"  ✅ {field}: {stats['meaningful_rate']}% ({stats['category']})")
        
        print(f"\n⚠️ MODERATE FIELDS (20-50% meaningful):")
        for field, stats in analysis['moderate_fields'].items():
            print(f"  ⚠️ {field}: {stats['meaningful_rate']}% ({stats['category']})")
        
        print(f"\n❌ POOR FIELDS (<20% meaningful):")
        for field, stats in analysis['poor_fields'].items():
            print(f"  ❌ {field}: {stats['meaningful_rate']}% ({stats['category']})")
            if stats['sample_values']:
                print(f"     Sample: {stats['sample_values'][0]}")
        
        print(f"\n🎨 UI RECOMMENDATIONS:")
        for rec in analysis['ui_recommendations']:
            print(f"  • {rec}")
        
        print(f"\n🔧 BACKEND ENRICHMENT PRIORITIES:")
        for priority in analysis['backend_priorities']:
            print(f"  • {priority}")

def main():
    try:
        analyzer = SupabaseFieldAnalyzer()
        
        # Run analysis
        analysis = analyzer.analyze_field_population(limit=500)
        
        if analysis:
            # Print results
            analyzer.print_analysis(analysis)
            
            # Save results
            output_file = 'supabase_field_analysis.json'
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            print(f"\n💾 Analysis saved to: {output_file}")
            print(f"✅ Analysis completed successfully using Supabase client (RLS-compatible)")
            
        else:
            print("❌ Analysis failed - check RLS policies and credentials")
            
    except Exception as e:
        print(f"❌ Script failed: {e}")
        print("💡 Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set in environment")

if __name__ == "__main__":
    main()
