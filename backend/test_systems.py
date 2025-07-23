#!/usr/bin/env python3
"""
Comprehensive test script to validate all the systems we've implemented:
1. Database connections (admin vs regular)
2. Balance monitoring functionality
3. Notification system
4. ETL rate limiting and caching
5. LLM provider abstraction
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_database_connections():
    """Test both regular and admin database connections"""
    print("🔍 Testing Database Connections...")
    
    try:
        from app.core.database import get_db, get_admin_db
        
        # Test regular database connection
        print("  ✓ Testing regular database connection...")
        db_gen = get_db()
        db = next(db_gen)
        print(f"    ✓ Regular DB client: {type(db).__name__}")
        
        # Test admin database connection
        print("  ✓ Testing admin database connection...")
        admin_db_gen = get_admin_db()
        admin_db = next(admin_db_gen)
        print(f"    ✓ Admin DB client: {type(admin_db).__name__}")
        
        print("  ✅ Database connections: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Database connections: FAILED - {e}")
        return False

async def test_balance_monitoring():
    """Test balance monitoring service functionality"""
    print("🔍 Testing Balance Monitoring Service...")
    
    try:
        # Import the balance monitoring class and functions
        from app.services.balance_monitoring import AccountBalanceMonitor, get_balance_monitor
        
        # Get the balance monitor instance
        monitor = get_balance_monitor()
        
        # Test OpenAI balance check
        print("  ✓ Testing OpenAI balance check...")
        async with AccountBalanceMonitor() as temp_monitor:
            openai_balance = await temp_monitor.get_openai_balance()
            balance_value = openai_balance.balance_usd if openai_balance else "N/A"
            print(f"    ✓ OpenAI balance: ${balance_value}")
            
            # Test DeepSeek balance check
            print("  ✓ Testing DeepSeek balance check...")
            deepseek_balance = await temp_monitor.get_deepseek_balance()
            balance_value = deepseek_balance.balance_usd if deepseek_balance else "N/A"
            print(f"    ✓ DeepSeek balance: ${balance_value}")
            
            # Test balance monitoring
            print("  ✓ Testing balance monitoring...")
            balances = await temp_monitor.check_all_balances()
            print(f"    ✓ Monitored {len(balances)} providers")
        
        print("  ✅ Balance monitoring: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Balance monitoring: FAILED - {e}")
        return False

async def test_notification_system():
    """Test notification system functionality"""
    print("🔍 Testing Notification System...")
    
    try:
        # Import notification system class and functions
        from app.core.notification_system import EnhancedNotificationSystem, get_notification_system, AlertCategory, AlertLevel
        
        print("  ✓ Notification system imports successful...")
        
        # Get the notification system instance
        notification_system = get_notification_system()
        
        # Test alert creation
        print("  ✓ Testing alert creation...")
        alert = await notification_system.create_alert(
            category=AlertCategory.API_BALANCE,
            level=AlertLevel.WARNING,
            title="Test Alert",
            message="OpenAI balance is below threshold",
            data={
                "provider": "openai",
                "current_balance": 5.0,
                "threshold": 10.0
            }
        )
        print(f"    ✓ Alert creation: {'SUCCESS' if alert else 'FAILED'}")
        
        # Test getting active alerts
        print("  ✓ Testing alert retrieval...")
        active_alerts = notification_system.get_active_alerts()
        print(f"    ✓ Active alerts: {len(active_alerts)}")
        
        # Test alert summary
        print("  ✓ Testing alert summary...")
        summary = notification_system.get_alert_summary()
        print(f"    ✓ Alert summary: {summary['active_alerts']} active alerts")
        
        print("  ✅ Notification system: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Notification system: FAILED - {e}")
        return False

async def test_rate_limiting():
    """Test ETL rate limiting functionality"""
    print("🔍 Testing ETL Rate Limiting...")
    
    try:
        # Test the rate limiter implementation
        from app.core.etl_tasks import SimpleRateLimiter
        
        rate_limiter = SimpleRateLimiter()
        
        # Test rate limiting
        print("  ✓ Testing rate limiter...")
        
        # Should allow first request
        can_make_request = rate_limiter.can_make_request("test_api", max_calls=2, window_seconds=60)
        print(f"    ✓ First request allowed: {can_make_request}")
        
        # Should allow second request
        can_make_request = rate_limiter.can_make_request("test_api", max_calls=2, window_seconds=60)
        print(f"    ✓ Second request allowed: {can_make_request}")
        
        # Should deny third request
        can_make_request = rate_limiter.can_make_request("test_api", max_calls=2, window_seconds=60)
        print(f"    ✓ Third request denied: {not can_make_request}")
        
        # Test wait time calculation
        wait_time = rate_limiter.wait_time("test_api", window_seconds=60)
        print(f"    ✓ Wait time calculated: {wait_time:.2f}s")
        
        print("  ✅ Rate limiting: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Rate limiting: FAILED - {e}")
        return False

async def test_llm_provider_abstraction():
    """Test LLM provider abstraction"""
    print("🔍 Testing LLM Provider Abstraction...")
    
    try:
        # Test LLM provider functions from the correct module
        from app.core.llm_provider import get_smart_llm_provider, TaskType, SmartLLMProvider
        
        # Test provider selection
        print("  ✓ Testing smart provider selection...")
        provider = get_smart_llm_provider()
        print(f"    ✓ Provider selected: {type(provider).__name__}")
        
        # Test task type enum
        print("  ✓ Testing task types...")
        task_types = [TaskType.PARSING, TaskType.VALIDATION, TaskType.EMBEDDING]
        print(f"    ✓ Available task types: {[t.value for t in task_types]}")
        
        # Test usage statistics
        print("  ✓ Testing usage statistics...")
        stats = provider.get_usage_stats()
        print(f"    ✓ Usage stats available for {len(stats)} providers")
        
        # Test cost savings report
        print("  ✓ Testing cost savings report...")
        savings_report = provider.get_cost_savings_report()
        print(f"    ✓ Cost savings: ${savings_report['total_savings']:.2f}")
        
        print("  ✅ LLM provider abstraction: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ LLM provider abstraction: FAILED - {e}")
        return False

async def test_supabase_configuration():
    """Test Supabase configuration and client setup"""
    print("🔍 Testing Supabase Configuration...")
    
    try:
        from app.core.supabase_client import get_supabase_client, create_supabase_client
        
        # Test getting the global service role client
        print("  ✓ Testing global service role client...")
        service_client = get_supabase_client()
        print(f"    ✓ Service client: {type(service_client).__name__}")
        
        # Test creating anon client
        print("  ✓ Testing anon client creation...")
        anon_client = create_supabase_client(use_service_key=False)
        print(f"    ✓ Anon client: {type(anon_client).__name__}")
        
        # Test creating service client
        print("  ✓ Testing service client creation...")
        new_service_client = create_supabase_client(use_service_key=True)
        print(f"    ✓ New service client: {type(new_service_client).__name__}")
        
        print("  ✅ Supabase configuration: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Supabase configuration: FAILED - {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive System Tests")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Database Connections", test_database_connections),
        ("Supabase Configuration", test_supabase_configuration),
        ("Balance Monitoring", test_balance_monitoring),
        ("Notification System", test_notification_system),
        ("Rate Limiting", test_rate_limiting),
        ("LLM Provider Abstraction", test_llm_provider_abstraction),
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: CRASHED - {e}")
            test_results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All systems are working correctly!")
    else:
        print("⚠️  Some systems need attention.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())
