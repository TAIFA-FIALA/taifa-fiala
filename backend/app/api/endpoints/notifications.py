"""
Notification System API Endpoints
Provides API access to the enhanced notification system for monitoring alerts
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.core.notification_system import (
    get_notification_system, 
    AlertLevel, 
    AlertCategory, 
    Alert,
    LLMUsageThresholds,
    APIBalanceThresholds
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/notifications", tags=["notifications"])

class AlertResponse(BaseModel):
    """API response model for alerts"""
    id: str
    category: str
    level: str
    title: str
    message: str
    timestamp: datetime
    data: Dict[str, Any]
    resolved: bool
    resolved_at: Optional[datetime]

class AlertSummaryResponse(BaseModel):
    """API response model for alert summary"""
    active_alerts: int
    alerts_by_level: Dict[str, int]
    alerts_by_category: Dict[str, int]
    monitoring_active: bool
    notification_channels: int
    enabled_channels: int

class ThresholdUpdateRequest(BaseModel):
    """Request model for updating monitoring thresholds"""
    llm_thresholds: Optional[Dict[str, float]] = None
    balance_thresholds: Optional[Dict[str, float]] = None

@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    category: Optional[AlertCategory] = Query(None, description="Filter by alert category"),
    level: Optional[AlertLevel] = Query(None, description="Filter by alert level"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of alerts to return")
):
    """Get alerts with optional filtering"""
    try:
        notification_system = get_notification_system()
        
        # Get active alerts (or all if resolved filter is specified)
        if resolved is None:
            alerts = notification_system.get_active_alerts(category)
        else:
            all_alerts = list(notification_system.active_alerts.values())
            if category:
                all_alerts = [a for a in all_alerts if a.category == category]
            alerts = [a for a in all_alerts if a.resolved == resolved]
        
        # Filter by level if specified
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        # Limit results
        alerts = alerts[:limit]
        
        # Convert to response format
        response = []
        for alert in alerts:
            response.append(AlertResponse(
                id=alert.id,
                category=alert.category.value,
                level=alert.level.value,
                title=alert.title,
                message=alert.message,
                timestamp=alert.timestamp,
                data=alert.data,
                resolved=alert.resolved,
                resolved_at=alert.resolved_at
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")

@router.get("/alerts/summary", response_model=AlertSummaryResponse)
async def get_alert_summary():
    """Get summary of alert system status"""
    try:
        notification_system = get_notification_system()
        summary = notification_system.get_alert_summary()
        
        return AlertSummaryResponse(**summary)
        
    except Exception as e:
        logger.error(f"Failed to get alert summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alert summary: {str(e)}")

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark an alert as resolved"""
    try:
        notification_system = get_notification_system()
        success = notification_system.resolve_alert(alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        return {"message": f"Alert {alert_id} resolved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")

@router.post("/alerts/create")
async def create_manual_alert(
    category: AlertCategory,
    level: AlertLevel,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
):
    """Create a manual alert (admin function)"""
    try:
        notification_system = get_notification_system()
        alert = await notification_system.create_alert(category, level, title, message, data)
        
        return {
            "message": "Alert created successfully",
            "alert_id": alert.id,
            "alert": AlertResponse(
                id=alert.id,
                category=alert.category.value,
                level=alert.level.value,
                title=alert.title,
                message=alert.message,
                timestamp=alert.timestamp,
                data=alert.data,
                resolved=alert.resolved,
                resolved_at=alert.resolved_at
            )
        }
        
    except Exception as e:
        logger.error(f"Failed to create alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")

@router.post("/monitoring/start")
async def start_monitoring(
    background_tasks: BackgroundTasks,
    check_interval_minutes: int = Query(15, ge=1, le=60, description="Monitoring check interval in minutes")
):
    """Start continuous monitoring"""
    try:
        notification_system = get_notification_system()
        
        if notification_system.monitoring_active:
            return {"message": "Monitoring is already active"}
        
        # Start monitoring in background
        background_tasks.add_task(notification_system.start_monitoring, check_interval_minutes)
        
        return {
            "message": f"Monitoring started with {check_interval_minutes} minute intervals",
            "check_interval_minutes": check_interval_minutes
        }
        
    except Exception as e:
        logger.error(f"Failed to start monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

@router.post("/monitoring/stop")
async def stop_monitoring():
    """Stop continuous monitoring"""
    try:
        notification_system = get_notification_system()
        notification_system.stop_monitoring()
        
        return {"message": "Monitoring stopped successfully"}
        
    except Exception as e:
        logger.error(f"Failed to stop monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")

@router.get("/monitoring/status")
async def get_monitoring_status():
    """Get current monitoring status"""
    try:
        notification_system = get_notification_system()
        
        return {
            "monitoring_active": notification_system.monitoring_active,
            "notification_channels": len(notification_system.channels),
            "enabled_channels": len([c for c in notification_system.channels.values() if c.enabled]),
            "channel_names": list(notification_system.channels.keys()),
            "thresholds": {
                "llm_usage": notification_system.llm_thresholds.dict(),
                "api_balance": notification_system.balance_thresholds.dict()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitoring status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve monitoring status: {str(e)}")

@router.put("/monitoring/thresholds")
async def update_thresholds(request: ThresholdUpdateRequest):
    """Update monitoring thresholds"""
    try:
        notification_system = get_notification_system()
        
        updated = []
        
        # Update LLM thresholds
        if request.llm_thresholds:
            for key, value in request.llm_thresholds.items():
                if hasattr(notification_system.llm_thresholds, key):
                    setattr(notification_system.llm_thresholds, key, value)
                    updated.append(f"llm_thresholds.{key}")
        
        # Update balance thresholds
        if request.balance_thresholds:
            for key, value in request.balance_thresholds.items():
                if hasattr(notification_system.balance_thresholds, key):
                    setattr(notification_system.balance_thresholds, key, value)
                    updated.append(f"balance_thresholds.{key}")
        
        return {
            "message": f"Updated {len(updated)} thresholds",
            "updated_thresholds": updated,
            "current_thresholds": {
                "llm_usage": notification_system.llm_thresholds.dict(),
                "api_balance": notification_system.balance_thresholds.dict()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to update thresholds: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update thresholds: {str(e)}")

@router.post("/monitoring/check-now")
async def trigger_monitoring_check():
    """Manually trigger a monitoring check"""
    try:
        notification_system = get_notification_system()
        
        # Run monitoring checks
        llm_alerts = await notification_system.monitor_llm_usage()
        balance_alerts = await notification_system.check_api_balances()
        
        total_alerts = len(llm_alerts) + len(balance_alerts)
        
        return {
            "message": "Monitoring check completed",
            "alerts_generated": total_alerts,
            "llm_alerts": len(llm_alerts),
            "balance_alerts": len(balance_alerts),
            "alert_ids": [alert.id for alert in llm_alerts + balance_alerts]
        }
        
    except Exception as e:
        logger.error(f"Failed to run monitoring check: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run monitoring check: {str(e)}")

@router.get("/channels")
async def get_notification_channels():
    """Get information about configured notification channels"""
    try:
        notification_system = get_notification_system()
        
        channels_info = {}
        for name, channel in notification_system.channels.items():
            channels_info[name] = {
                "name": channel.name,
                "enabled": channel.enabled,
                "min_level": channel.min_level.value,
                "config_keys": list(channel.config.keys()) if channel.config else []
            }
        
        return {
            "channels": channels_info,
            "total_channels": len(notification_system.channels),
            "enabled_channels": len([c for c in notification_system.channels.values() if c.enabled])
        }
        
    except Exception as e:
        logger.error(f"Failed to get notification channels: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve notification channels: {str(e)}")

@router.post("/test-notification")
async def send_test_notification(
    level: AlertLevel = AlertLevel.INFO,
    channel: Optional[str] = Query(None, description="Specific channel to test (optional)")
):
    """Send a test notification to verify channel configuration"""
    try:
        notification_system = get_notification_system()
        
        # Create a test alert
        alert = await notification_system.create_alert(
            AlertCategory.SYSTEM_PERFORMANCE,
            level,
            "Test Notification",
            f"This is a test notification sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} to verify the notification system is working correctly.",
            {"test": True, "requested_channel": channel}
        )
        
        return {
            "message": "Test notification sent successfully",
            "alert_id": alert.id,
            "level": level.value,
            "channels_notified": list(notification_system.channels.keys()) if not channel else [channel]
        }
        
    except Exception as e:
        logger.error(f"Failed to send test notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send test notification: {str(e)}")
