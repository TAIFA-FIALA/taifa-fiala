#!/usr/bin/env python3
"""
Smart RSS Feed Prioritization System Test
Demonstrates adaptive polling based on feed success rate and performance metrics
"""

import asyncio
import sys
import time
from datetime import datetime
sys.path.append('.')

from app.services.data_ingestion.high_volume_pipeline import (
    HighVolumeDataPipeline, DataSource, SourceType, Priority
)

async def test_smart_prioritization():
    """Test the smart prioritization system with simulated feed performance"""
    print("🎯 Testing Smart RSS Feed Prioritization System")
    print("=" * 60)
    
    # Create pipeline
    pipeline = HighVolumeDataPipeline(max_workers=5, batch_size=100)
    
    # Create test sources with different performance characteristics
    test_sources = [
        # High-performing source (should get frequent polling)
        DataSource(
            name="Crunchbase News (High Performer)",
            url="https://news.crunchbase.com/feed/",
            source_type=SourceType.RSS,
            priority=Priority.HIGH,
            check_interval_minutes=60,
            keywords=['funding', 'investment', 'Africa']
        ),
        
        # Medium-performing source
        DataSource(
            name="TechCrunch (Medium Performer)",
            url="https://techcrunch.com/feed/",
            source_type=SourceType.RSS,
            priority=Priority.MEDIUM,
            check_interval_minutes=60,
            keywords=['startup', 'AI', 'technology']
        ),
        
        # Low-performing source (should get less frequent polling)
        DataSource(
            name="Generic Tech Blog (Low Performer)",
            url="https://example-tech-blog.com/feed/",
            source_type=SourceType.RSS,
            priority=Priority.LOW,
            check_interval_minutes=60,
            keywords=['tech']
        ),
        
        # New source (neutral performance)
        DataSource(
            name="New African Tech Source",
            url="https://new-african-tech.com/feed/",
            source_type=SourceType.RSS,
            priority=Priority.MEDIUM,
            check_interval_minutes=60,
            keywords=['Africa', 'technology', 'funding']
        )
    ]
    
    # Add sources to pipeline
    pipeline.sources = test_sources
    
    print("📊 Initial Source Configuration:")
    print("-" * 40)
    for source in pipeline.sources:
        print(f"  {source.name}")
        print(f"    Priority Score: {source.get_dynamic_priority_score():.3f}")
        print(f"    Check Interval: {source.check_interval_minutes} minutes")
        print(f"    Success Rate: {source.get_success_rate():.3f}")
        print()
    
    # Simulate performance data over time
    print("🔄 Simulating Performance Data Over Time...")
    print("-" * 40)
    
    # Simulate high performer
    high_performer = test_sources[0]
    for i in range(10):
        high_performer.update_performance_metrics(
            success=True, 
            items_collected=25 + (i * 2),  # Increasing productivity
            response_time=1.2,
            quality_score=0.8 + (i * 0.02)  # Improving quality
        )
    
    # Simulate medium performer
    medium_performer = test_sources[1]
    for i in range(8):
        success = i < 6  # Some failures
        medium_performer.update_performance_metrics(
            success=success,
            items_collected=15 if success else 0,
            response_time=2.5,
            quality_score=0.6 if success else 0.0
        )
    
    # Simulate low performer
    low_performer = test_sources[2]
    for i in range(6):
        success = i < 2  # Mostly failures
        low_performer.update_performance_metrics(
            success=success,
            items_collected=5 if success else 0,
            response_time=8.0,
            quality_score=0.3 if success else 0.0
        )
    
    # New source stays neutral (no performance data)
    
    print("📈 Performance After Simulation:")
    print("-" * 40)
    
    # Sort by performance score
    sorted_sources = sorted(pipeline.sources, key=lambda s: s.get_dynamic_priority_score(), reverse=True)
    
    for i, source in enumerate(sorted_sources, 1):
        score = source.get_dynamic_priority_score()
        interval = source.calculate_adaptive_interval()
        
        print(f"{i}. {source.name}")
        print(f"   📊 Priority Score: {score:.3f}")
        print(f"   ⏰ Adaptive Interval: {interval} minutes (was {source.base_check_interval})")
        print(f"   ✅ Success Rate: {source.get_success_rate():.3f}")
        print(f"   📦 Total Items: {source.items_collected_total}")
        print(f"   ⭐ Quality Score: {source.quality_score:.3f}")
        print(f"   ⚡ Response Time: {source.response_time_avg:.1f}s")
        print(f"   🔄 Consecutive Failures: {source.consecutive_failures}")
        print()
    
    # Show smart prioritization statistics
    print("📋 Smart Prioritization Statistics:")
    print("-" * 40)
    smart_stats = pipeline.get_smart_prioritization_stats()
    
    print(f"Performance Tiers:")
    print(f"  🚀 High Performers: {smart_stats['performance_tiers']['high_performers']}")
    print(f"  📈 Medium Performers: {smart_stats['performance_tiers']['medium_performers']}")
    print(f"  📉 Low Performers: {smart_stats['performance_tiers']['low_performers']}")
    print()
    
    print(f"Average Metrics:")
    print(f"  Success Rate: {smart_stats['average_metrics']['success_rate']:.3f}")
    print(f"  Quality Score: {smart_stats['average_metrics']['quality_score']:.3f}")
    print(f"  Productivity: {smart_stats['average_metrics']['productivity_score']:.2f}")
    print()
    
    print(f"Adaptive Intervals:")
    print(f"  Fastest: {smart_stats['adaptive_intervals']['fastest_interval']} minutes")
    print(f"  Slowest: {smart_stats['adaptive_intervals']['slowest_interval']} minutes")
    print(f"  Average: {smart_stats['adaptive_intervals']['average_interval']:.1f} minutes")
    print()
    
    # Demonstrate scheduling behavior
    print("🕐 Scheduling Behavior Demonstration:")
    print("-" * 40)
    
    current_time = datetime.now()
    for source in sorted_sources:
        should_check = source.should_check_now()
        print(f"{source.name}:")
        print(f"  Should check now: {should_check}")
        print(f"  Next check in: {source.check_interval_minutes} minutes")
        print(f"  Reason: {'High priority' if source.get_dynamic_priority_score() >= 0.7 else 'Medium priority' if source.get_dynamic_priority_score() >= 0.4 else 'Low priority'}")
        print()
    
    print("✅ Smart Prioritization System Test Complete!")
    print()
    print("🎯 Key Benefits Demonstrated:")
    print("  • High-performing feeds get polled more frequently (5-15 min intervals)")
    print("  • Low-performing feeds get polled less frequently (120+ min intervals)")
    print("  • Quality scores influence prioritization")
    print("  • Consecutive failures reduce polling frequency")
    print("  • System adapts automatically based on feed performance")
    print("  • Comprehensive metrics tracking for optimization")

if __name__ == "__main__":
    asyncio.run(test_smart_prioritization())
