"""
Account Balance Monitoring API Endpoints

Provides REST API endpoints for monitoring LLM provider account balances,
configuring alert thresholds, and retrieving balance information.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel

from app.services.balance_monitoring import (
    get_balance_monitor, 
    AccountBalance, 
    ProviderType, 
    BalanceAlert
)
from app.core.notification_system import get_notification_system, AlertCategory, AlertLevel
from app.core.database import get_admin_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/balance-monitoring", tags=["balance-monitoring"])


class BalanceResponse(BaseModel):
    """API response model for account balance"""
    provider: str
    balance_usd: float
    credit_limit_usd: Optional[float]
    usage_current_month_usd: float
    usage_last_30_days_usd: float
    last_updated: datetime
    status: str
    days_remaining: Optional[int]
    billing_cycle_start: Optional[datetime]
    billing_cycle_end: Optional[datetime]


class BalancesSummary(BaseModel):
    """Summary of all provider balances"""
    total_providers: int
    active_providers: int
    warning_providers: int
    critical_providers: int
    total_balance_usd: float
    total_monthly_usage_usd: float
    balances: List[BalanceResponse]
    alerts: List[Dict[str, Any]]
    last_updated: datetime


class AlertThresholdUpdate(BaseModel):
    """Request model for updating alert thresholds"""
    provider: str
    warning_threshold_usd: float
    critical_threshold_usd: float


class BalanceCheckResponse(BaseModel):
    """Response for balance check operations"""
    success: bool
    message: str
    providers_checked: List[str]
    alerts_generated: int
    timestamp: datetime


@router.get("/balances", response_model=BalancesSummary)
async def get_all_balances():
    """Get current balance information for all LLM providers"""
    try:
        monitor = get_balance_monitor()
        
        # Get cached balances first
        cached_balances = monitor.get_cached_balances()
        
        # If no cached data or data is old (>1 hour), refresh
        if not cached_balances or not monitor.last_check or \
           (datetime.utcnow() - monitor.last_check).total_seconds() > 3600:
            logger.info("Refreshing balance data...")
            async with monitor:
                cached_balances = await monitor.check_all_balances()
        
        # Convert to API response format
        balance_responses = []
        total_balance = 0.0
        total_usage = 0.0
        warning_count = 0
        critical_count = 0
        
        for provider_type, balance in cached_balances.items():
            balance_response = BalanceResponse(
                provider=provider_type.value,
                balance_usd=balance.balance_usd,
                credit_limit_usd=balance.credit_limit_usd,
                usage_current_month_usd=balance.usage_current_month_usd,
                usage_last_30_days_usd=balance.usage_last_30_days_usd,
                last_updated=balance.last_updated,
                status=balance.status,
                days_remaining=balance.days_remaining,
                billing_cycle_start=balance.billing_cycle_start,
                billing_cycle_end=balance.billing_cycle_end
            )
            balance_responses.append(balance_response)
            
            total_balance += balance.balance_usd
            total_usage += balance.usage_current_month_usd
            
            if balance.status == "warning":
                warning_count += 1
            elif balance.status == "critical":
                critical_count += 1
        
        # Get low balance alerts
        alerts = monitor.get_low_balance_alerts()
        
        summary = BalancesSummary(
            total_providers=len(cached_balances),
            active_providers=len(cached_balances) - warning_count - critical_count,
            warning_providers=warning_count,
            critical_providers=critical_count,
            total_balance_usd=total_balance,
            total_monthly_usage_usd=total_usage,
            balances=balance_responses,
            alerts=alerts,
            last_updated=monitor.last_check or datetime.utcnow()
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get balance information: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve balances: {str(e)}")


@router.get("/balances/{provider}", response_model=BalanceResponse)
async def get_provider_balance(provider: str):
    """Get balance information for a specific provider"""
    try:
        provider_type = ProviderType(provider.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
    
    try:
        monitor = get_balance_monitor()
        cached_balances = monitor.get_cached_balances()
        
        if provider_type not in cached_balances:
            # Try to fetch fresh data for this provider
            async with monitor:
                if provider_type == ProviderType.OPENAI:
                    balance = await monitor.get_openai_balance()
                elif provider_type == ProviderType.DEEPSEEK:
                    balance = await monitor.get_deepseek_balance()
                elif provider_type == ProviderType.GEMINI:
                    balance = await monitor.get_gemini_balance()
                else:
                    raise HTTPException(status_code=404, detail=f"Provider {provider} not found")
                
                if not balance:
                    raise HTTPException(status_code=404, detail=f"Balance data not available for {provider}")
        else:
            balance = cached_balances[provider_type]
        
        return BalanceResponse(
            provider=balance.provider.value,
            balance_usd=balance.balance_usd,
            credit_limit_usd=balance.credit_limit_usd,
            usage_current_month_usd=balance.usage_current_month_usd,
            usage_last_30_days_usd=balance.usage_last_30_days_usd,
            last_updated=balance.last_updated,
            status=balance.status,
            days_remaining=balance.days_remaining,
            billing_cycle_start=balance.billing_cycle_start,
            billing_cycle_end=balance.billing_cycle_end
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get balance for {provider}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve balance: {str(e)}")


@router.post("/check-balances", response_model=BalanceCheckResponse)
async def check_balances_now(background_tasks: BackgroundTasks):
    """Force immediate balance check for all providers"""
    try:
        monitor = get_balance_monitor()
        
        async with monitor:
            balances = await monitor.check_all_balances()
        
        # Generate alerts for low balances
        alerts = monitor.get_low_balance_alerts()
        alerts_generated = 0
        
        if alerts:
            # Send alerts via notification system
            notification_system = get_notification_system()
            
            for alert in alerts:
                alert_level = AlertLevel.CRITICAL if alert["level"] == "critical" else AlertLevel.WARNING
                
                await notification_system.create_alert(
                    category=AlertCategory.API_BALANCE,
                    level=alert_level,
                    title=f"Low Balance Alert: {alert['provider'].title()}",
                    message=alert["message"],
                    details={
                        "provider": alert["provider"],
                        "balance_usd": alert["balance_usd"],
                        "days_remaining": alert["days_remaining"]
                    }
                )
                alerts_generated += 1
        
        return BalanceCheckResponse(
            success=True,
            message=f"Successfully checked {len(balances)} providers",
            providers_checked=[provider.value for provider in balances.keys()],
            alerts_generated=alerts_generated,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to check balances: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check balances: {str(e)}")


@router.put("/thresholds", response_model=Dict[str, str])
async def update_alert_thresholds(threshold_update: AlertThresholdUpdate):
    """Update alert thresholds for a provider"""
    try:
        provider_type = ProviderType(threshold_update.provider.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {threshold_update.provider}")
    
    if threshold_update.warning_threshold_usd <= threshold_update.critical_threshold_usd:
        raise HTTPException(
            status_code=400, 
            detail="Warning threshold must be greater than critical threshold"
        )
    
    try:
        monitor = get_balance_monitor()
        monitor.update_alert_thresholds(
            provider_type,
            threshold_update.warning_threshold_usd,
            threshold_update.critical_threshold_usd
        )
        
        return {
            "message": f"Alert thresholds updated for {threshold_update.provider}",
            "provider": threshold_update.provider,
            "warning_threshold": str(threshold_update.warning_threshold_usd),
            "critical_threshold": str(threshold_update.critical_threshold_usd)
        }
        
    except Exception as e:
        logger.error(f"Failed to update thresholds: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update thresholds: {str(e)}")


@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_balance_alerts():
    """Get current low balance alerts"""
    try:
        monitor = get_balance_monitor()
        alerts = monitor.get_low_balance_alerts()
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to get balance alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")


@router.get("/health")
async def balance_monitoring_health():
    """Health check for balance monitoring service"""
    try:
        monitor = get_balance_monitor()
        cached_balances = monitor.get_cached_balances()
        
        health_status = {
            "status": "healthy",
            "providers_configured": len([p for p in ProviderType if getattr(settings, f"{p.value.upper()}_API_KEY", None)]),
            "providers_monitored": len(cached_balances),
            "last_check": monitor.last_check.isoformat() if monitor.last_check else None,
            "alerts_active": len(monitor.get_low_balance_alerts()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Balance monitoring health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
