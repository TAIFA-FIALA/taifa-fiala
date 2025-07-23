"""
Enhanced Notification System for TAIFA-FIALA
Handles alerts for LLM usage, API costs, account balances, and pipeline health
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from pydantic import BaseModel

from app.core.config import settings
from app.core.llm_provider import get_smart_llm_provider

logger = logging.getLogger(__name__)

class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertCategory(str, Enum):
    """Alert categories"""
    LLM_USAGE = "llm_usage"
    LLM_COST = "llm_cost"
    API_BALANCE = "api_balance"
    PIPELINE_HEALTH = "pipeline_health"
    SYSTEM_PERFORMANCE = "system_performance"
    DATA_QUALITY = "data_quality"

@dataclass
class Alert:
    """Individual alert data structure"""
    id: str
    category: AlertCategory
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category.value,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }

@dataclass
class NotificationChannel:
    """Notification delivery channel configuration"""
    name: str
    enabled: bool
    config: Dict[str, Any]
    min_level: AlertLevel = AlertLevel.WARNING

class LLMUsageThresholds(BaseModel):
    """LLM usage monitoring thresholds"""
    daily_cost_warning: float = 10.0  # USD
    daily_cost_critical: float = 50.0  # USD
    hourly_requests_warning: int = 100
    hourly_requests_critical: int = 500
    failure_rate_warning: float = 0.1  # 10%
    failure_rate_critical: float = 0.25  # 25%
    response_time_warning: float = 5000.0  # ms
    response_time_critical: float = 10000.0  # ms

class APIBalanceThresholds(BaseModel):
    """API account balance monitoring thresholds"""
    openai_balance_warning: float = 10.0  # USD
    openai_balance_critical: float = 5.0  # USD
    deepseek_balance_warning: float = 5.0  # USD
    deepseek_balance_critical: float = 2.0  # USD
    serper_quota_warning: int = 100  # remaining searches
    serper_quota_critical: int = 20  # remaining searches

class EnhancedNotificationSystem:
    """Comprehensive notification system for TAIFA-FIALA monitoring"""
    
    def __init__(self):
        self.channels: Dict[str, NotificationChannel] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.llm_thresholds = LLMUsageThresholds()
        self.balance_thresholds = APIBalanceThresholds()
        self.monitoring_active = False
        
        # Initialize notification channels
        self._setup_notification_channels()
        
        logger.info("Enhanced notification system initialized")
    
    def _setup_notification_channels(self):
        """Setup available notification channels"""
        
        # Email notifications
        if hasattr(settings, 'SMTP_HOST') and settings.SMTP_HOST:
            self.channels['email'] = NotificationChannel(
                name="email",
                enabled=True,
                config={
                    'smtp_host': settings.SMTP_HOST,
                    'smtp_port': getattr(settings, 'SMTP_PORT', 587),
                    'smtp_user': getattr(settings, 'SMTP_USER', ''),
                    'smtp_password': getattr(settings, 'SMTP_PASSWORD', ''),
                    'from_email': getattr(settings, 'NOTIFICATION_FROM_EMAIL', 'alerts@taifa-fiala.net'),
                    'to_emails': getattr(settings, 'NOTIFICATION_TO_EMAILS', '').split(',')
                },
                min_level=AlertLevel.WARNING
            )
        
        # Slack notifications
        if hasattr(settings, 'SLACK_WEBHOOK_URL') and settings.SLACK_WEBHOOK_URL:
            self.channels['slack'] = NotificationChannel(
                name="slack",
                enabled=True,
                config={'webhook_url': settings.SLACK_WEBHOOK_URL},
                min_level=AlertLevel.WARNING
            )
        
        # n8n webhook notifications
        if hasattr(settings, 'N8N_WEBHOOK_URL') and settings.N8N_WEBHOOK_URL:
            self.channels['n8n'] = NotificationChannel(
                name="n8n",
                enabled=True,
                config={'webhook_url': settings.N8N_WEBHOOK_URL},
                min_level=AlertLevel.INFO
            )
        
        # Console notifications (always enabled)
        self.channels['console'] = NotificationChannel(
            name="console",
            enabled=True,
            config={},
            min_level=AlertLevel.INFO
        )
        
        logger.info(f"Initialized {len(self.channels)} notification channels: {list(self.channels.keys())}")
    
    async def create_alert(
        self, 
        category: AlertCategory, 
        level: AlertLevel, 
        title: str, 
        message: str, 
        data: Dict[str, Any] = None
    ) -> Alert:
        """Create and process a new alert"""
        
        alert_id = f"{category.value}_{level.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert = Alert(
            id=alert_id,
            category=category,
            level=level,
            title=title,
            message=message,
            timestamp=datetime.now(),
            data=data or {}
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        await self._send_notifications(alert)
        
        logger.info(f"Created {level.value} alert: {title}")
        return alert
    
    async def _send_notifications(self, alert: Alert):
        """Send alert through all appropriate channels"""
        
        for channel_name, channel in self.channels.items():
            if not channel.enabled:
                continue
                
            # Check if alert level meets channel minimum
            level_priority = {
                AlertLevel.INFO: 1,
                AlertLevel.WARNING: 2,
                AlertLevel.ERROR: 3,
                AlertLevel.CRITICAL: 4
            }
            
            if level_priority[alert.level] < level_priority[channel.min_level]:
                continue
            
            try:
                if channel_name == 'email':
                    await self._send_email_notification(alert, channel)
                elif channel_name == 'slack':
                    await self._send_slack_notification(alert, channel)
                elif channel_name == 'n8n':
                    await self._send_n8n_webhook_notification(alert, channel)
                elif channel_name == 'console':
                    await self._send_console_notification(alert, channel)
                    
            except Exception as e:
                logger.error(f"Failed to send notification via {channel_name}: {e}")
    
    async def _send_email_notification(self, alert: Alert, channel: NotificationChannel):
        """Send email notification"""
        config = channel.config
        
        if not config.get('to_emails') or not config['to_emails'][0]:
            return
        
        msg = MIMEMultipart()
        msg['From'] = config['from_email']
        msg['To'] = ', '.join(config['to_emails'])
        msg['Subject'] = f"[TAIFA-FIALA {alert.level.upper()}] {alert.title}"
        
        body = f"""
        TAIFA-FIALA Alert Notification
        
        Level: {alert.level.upper()}
        Category: {alert.category.value}
        Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        {alert.message}
        
        Additional Data:
        {json.dumps(alert.data, indent=2) if alert.data else 'None'}
        
        ---
        This is an automated alert from the TAIFA-FIALA monitoring system.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(config['smtp_host'], config['smtp_port'])
            server.starttls()
            if config['smtp_user']:
                server.login(config['smtp_user'], config['smtp_password'])
            server.send_message(msg)
            server.quit()
            logger.debug(f"Email notification sent for alert {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _send_slack_notification(self, alert: Alert, channel: NotificationChannel):
        """Send Slack notification"""
        webhook_url = channel.config['webhook_url']
        
        # Color coding for different alert levels
        colors = {
            AlertLevel.INFO: "#36a64f",      # green
            AlertLevel.WARNING: "#ff9500",   # orange
            AlertLevel.ERROR: "#ff0000",     # red
            AlertLevel.CRITICAL: "#8b0000"   # dark red
        }
        
        payload = {
            "attachments": [{
                "color": colors.get(alert.level, "#36a64f"),
                "title": f"TAIFA-FIALA Alert: {alert.title}",
                "text": alert.message,
                "fields": [
                    {"title": "Level", "value": alert.level.upper(), "short": True},
                    {"title": "Category", "value": alert.category.value, "short": True},
                    {"title": "Time", "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'), "short": False}
                ],
                "footer": "TAIFA-FIALA Monitoring System",
                "ts": int(alert.timestamp.timestamp())
            }]
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.debug(f"Slack notification sent for alert {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    async def _send_console_notification(self, alert: Alert, channel: NotificationChannel):
        """Send console log notification"""
        log_level_map = {
            AlertLevel.INFO: logger.info,
            AlertLevel.WARNING: logger.warning,
            AlertLevel.ERROR: logger.error,
            AlertLevel.CRITICAL: logger.critical
        }
        
        log_func = log_level_map.get(alert.level, logger.info)
        log_func(f"[{alert.category.value.upper()}] {alert.title}: {alert.message}")
    
    async def _send_n8n_webhook_notification(self, alert: Alert, channel: NotificationChannel):
        """Send n8n webhook notification"""
        webhook_url = channel.config.get('webhook_url')
        if not webhook_url:
            logger.error("n8n webhook URL not configured")
            return
        
        # Create structured payload for n8n
        payload = {
            "alert_id": alert.id,
            "category": alert.category.value,
            "level": alert.level.value,
            "title": alert.title,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "data": alert.data,
            "resolved": alert.resolved,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "source": "taifa-fiala-backend",
            "environment": getattr(settings, 'ENVIRONMENT', 'production')
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'TAIFA-FIALA-Notifications/1.0'
                },
                timeout=30
            )
            response.raise_for_status()
            logger.debug(f"n8n webhook notification sent for alert {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send n8n webhook notification: {e}")
    
    async def monitor_llm_usage(self) -> List[Alert]:
        """Monitor LLM usage and create alerts if thresholds are exceeded"""
        alerts = []
        
        try:
            smart_provider = get_smart_llm_provider()
            usage_stats = smart_provider.get_usage_stats()
            
            for provider_name, stats in usage_stats.items():
                # Check failure rate
                if stats.success_rate < (1 - self.llm_thresholds.failure_rate_critical):
                    alert = await self.create_alert(
                        AlertCategory.LLM_USAGE,
                        AlertLevel.CRITICAL,
                        f"High {provider_name} failure rate",
                        f"{provider_name} has a {(1-stats.success_rate)*100:.1f}% failure rate (threshold: {self.llm_thresholds.failure_rate_critical*100:.1f}%)",
                        {"provider": provider_name, "success_rate": stats.success_rate, "total_requests": stats.total_requests}
                    )
                    alerts.append(alert)
                elif stats.success_rate < (1 - self.llm_thresholds.failure_rate_warning):
                    alert = await self.create_alert(
                        AlertCategory.LLM_USAGE,
                        AlertLevel.WARNING,
                        f"Elevated {provider_name} failure rate",
                        f"{provider_name} has a {(1-stats.success_rate)*100:.1f}% failure rate (threshold: {self.llm_thresholds.failure_rate_warning*100:.1f}%)",
                        {"provider": provider_name, "success_rate": stats.success_rate, "total_requests": stats.total_requests}
                    )
                    alerts.append(alert)
                
                # Check response time
                if stats.avg_response_time_ms > self.llm_thresholds.response_time_critical:
                    alert = await self.create_alert(
                        AlertCategory.LLM_USAGE,
                        AlertLevel.CRITICAL,
                        f"Slow {provider_name} response time",
                        f"{provider_name} average response time is {stats.avg_response_time_ms:.0f}ms (threshold: {self.llm_thresholds.response_time_critical:.0f}ms)",
                        {"provider": provider_name, "avg_response_time_ms": stats.avg_response_time_ms}
                    )
                    alerts.append(alert)
                elif stats.avg_response_time_ms > self.llm_thresholds.response_time_warning:
                    alert = await self.create_alert(
                        AlertCategory.LLM_USAGE,
                        AlertLevel.WARNING,
                        f"Elevated {provider_name} response time",
                        f"{provider_name} average response time is {stats.avg_response_time_ms:.0f}ms (threshold: {self.llm_thresholds.response_time_warning:.0f}ms)",
                        {"provider": provider_name, "avg_response_time_ms": stats.avg_response_time_ms}
                    )
                    alerts.append(alert)
                
                # Check daily cost (estimate based on current usage)
                daily_cost_estimate = stats.estimated_cost_usd * 24  # Rough daily estimate
                if daily_cost_estimate > self.llm_thresholds.daily_cost_critical:
                    alert = await self.create_alert(
                        AlertCategory.LLM_COST,
                        AlertLevel.CRITICAL,
                        f"High {provider_name} daily cost",
                        f"{provider_name} estimated daily cost is ${daily_cost_estimate:.2f} (threshold: ${self.llm_thresholds.daily_cost_critical:.2f})",
                        {"provider": provider_name, "estimated_daily_cost": daily_cost_estimate, "current_cost": stats.estimated_cost_usd}
                    )
                    alerts.append(alert)
                elif daily_cost_estimate > self.llm_thresholds.daily_cost_warning:
                    alert = await self.create_alert(
                        AlertCategory.LLM_COST,
                        AlertLevel.WARNING,
                        f"Elevated {provider_name} daily cost",
                        f"{provider_name} estimated daily cost is ${daily_cost_estimate:.2f} (threshold: ${self.llm_thresholds.daily_cost_warning:.2f})",
                        {"provider": provider_name, "estimated_daily_cost": daily_cost_estimate, "current_cost": stats.estimated_cost_usd}
                    )
                    alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error monitoring LLM usage: {e}")
            alert = await self.create_alert(
                AlertCategory.SYSTEM_PERFORMANCE,
                AlertLevel.ERROR,
                "LLM monitoring error",
                f"Failed to monitor LLM usage: {str(e)}",
                {"error": str(e)}
            )
            alerts.append(alert)
        
        return alerts
    
    async def check_api_balances(self) -> List[Alert]:
        """Check API account balances and create alerts for low balances using the balance monitoring service"""
        alerts = []
        
        try:
            # Import here to avoid circular imports
            from app.services.balance_monitoring import get_balance_monitor
            
            monitor = get_balance_monitor()
            
            # Check all balances using the dedicated service
            async with monitor:
                balances = await monitor.check_all_balances()
            
            # Generate alerts for low balances
            balance_alerts = monitor.get_low_balance_alerts()
            
            for alert_data in balance_alerts:
                level = AlertLevel.CRITICAL if alert_data["level"] == "critical" else AlertLevel.WARNING
                
                alert = await self.create_alert(
                    category=AlertCategory.API_BALANCE,
                    level=level,
                    title=f"Low Balance Alert: {alert_data['provider'].title()}",
                    message=alert_data["message"],
                    details={
                        "provider": alert_data["provider"],
                        "current_balance": alert_data["balance_usd"],
                        "status": alert_data["status"],
                        "days_remaining": alert_data["days_remaining"],
                        "last_updated": alert_data["last_updated"]
                    }
                )
                alerts.append(alert)
                
            logger.info(f"Balance monitoring completed: {len(balances)} providers checked, {len(balance_alerts)} alerts generated")
        
        except Exception as e:
            logger.error(f"Error checking API balances: {e}")
            alert = await self.create_alert(
                AlertCategory.SYSTEM_PERFORMANCE,
                AlertLevel.ERROR,
                "API balance monitoring error",
                f"Failed to check API balances: {str(e)}",
                {"error": str(e)}
            )
            alerts.append(alert)
        
        return alerts
    
    async def _check_openai_balance(self) -> Optional[float]:
        """Check OpenAI account balance (placeholder implementation)"""
        # TODO: Implement actual OpenAI balance checking
        # This would require calling OpenAI's billing API
        logger.debug("OpenAI balance check not implemented yet")
        return None
    
    async def _check_deepseek_balance(self) -> Optional[float]:
        """Check DeepSeek account balance (placeholder implementation)"""
        # TODO: Implement actual DeepSeek balance checking
        # This would require calling DeepSeek's billing API
        logger.debug("DeepSeek balance check not implemented yet")
        return None
    
    async def start_monitoring(self, check_interval_minutes: int = 15):
        """Start continuous monitoring with specified interval"""
        self.monitoring_active = True
        logger.info(f"Starting notification monitoring with {check_interval_minutes} minute intervals")
        
        while self.monitoring_active:
            try:
                # Monitor LLM usage
                llm_alerts = await self.monitor_llm_usage()
                
                # Check API balances
                balance_alerts = await self.check_api_balances()
                
                # Log monitoring cycle completion
                total_alerts = len(llm_alerts) + len(balance_alerts)
                if total_alerts > 0:
                    logger.info(f"Monitoring cycle completed: {total_alerts} alerts generated")
                else:
                    logger.debug("Monitoring cycle completed: no alerts")
                
                # Wait for next check
                await asyncio.sleep(check_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logger.info("Notification monitoring stopped")
    
    def get_active_alerts(self, category: Optional[AlertCategory] = None) -> List[Alert]:
        """Get all active (unresolved) alerts, optionally filtered by category"""
        alerts = [alert for alert in self.active_alerts.values() if not alert.resolved]
        
        if category:
            alerts = [alert for alert in alerts if alert.category == category]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            self.active_alerts[alert_id].resolved_at = datetime.now()
            logger.info(f"Alert {alert_id} marked as resolved")
            return True
        return False
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alert system status"""
        active_alerts = self.get_active_alerts()
        
        summary = {
            "active_alerts": len(active_alerts),
            "alerts_by_level": {},
            "alerts_by_category": {},
            "monitoring_active": self.monitoring_active,
            "notification_channels": len(self.channels),
            "enabled_channels": len([c for c in self.channels.values() if c.enabled])
        }
        
        for alert in active_alerts:
            # Count by level
            level = alert.level.value
            summary["alerts_by_level"][level] = summary["alerts_by_level"].get(level, 0) + 1
            
            # Count by category
            category = alert.category.value
            summary["alerts_by_category"][category] = summary["alerts_by_category"].get(category, 0) + 1
        
        return summary

# Global notification system instance
_notification_system: Optional[EnhancedNotificationSystem] = None

def get_notification_system() -> EnhancedNotificationSystem:
    """Get or create the global notification system instance"""
    global _notification_system
    if _notification_system is None:
        _notification_system = EnhancedNotificationSystem()
    return _notification_system
