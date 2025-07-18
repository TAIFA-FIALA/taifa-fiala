"""
Comprehensive Monitoring and Alerting System for Data Pipeline Health
Designed for production-grade monitoring of high-volume data pipelines

This module provides comprehensive monitoring capabilities:
- Real-time pipeline health monitoring
- Performance metrics collection and analysis
- Automated alerting for critical issues
- Resource usage monitoring
- Data quality monitoring
- SLA and threshold management
- Historical trend analysis
- Dashboard data generation
- Integration with external monitoring systems

Key Features:
- Multi-level alerting (INFO, WARNING, CRITICAL)
- Configurable thresholds and SLAs
- Integration with Slack, email, webhooks
- Prometheus metrics export
- Grafana dashboard support
- Anomaly detection
- Predictive alerting
- Comprehensive logging
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta
import json
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass, field
from enum import Enum
import requests
import psutil
import os
from collections import defaultdict, deque
import statistics
from pathlib import Path
import sqlite3
from contextlib import contextmanager
import aiohttp
import asyncpg
from prometheus_client import Counter, Gauge, Histogram, Summary, start_http_server
import numpy as np
from sklearn.ensemble import IsolationForest
import pickle
import traceback

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(Enum):
    """Types of metrics to monitor"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"
    PERCENTAGE = "percentage"


class HealthStatus(Enum):
    """Overall system health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class Threshold:
    """Threshold configuration for metrics"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    comparison_operator: str = ">"  # >, <, >=, <=, ==, !=
    evaluation_window: int = 5  # minutes
    consecutive_violations: int = 3
    enabled: bool = True


@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    alert_level: AlertLevel
    title: str
    description: str
    metric_name: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.alert_level, str):
            self.alert_level = AlertLevel(self.alert_level)


@dataclass
class Metric:
    """Metric data structure"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    
    def __post_init__(self):
        if isinstance(self.metric_type, str):
            self.metric_type = MetricType(self.metric_type)


@dataclass
class SLA:
    """Service Level Agreement configuration"""
    name: str
    target_percentage: float
    measurement_window: int = 24  # hours
    metric_name: str = ""
    success_condition: str = ""
    enabled: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring system configuration"""
    # Alert channels
    slack_webhook_url: Optional[str] = None
    email_smtp_server: Optional[str] = None
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_recipients: List[str] = field(default_factory=list)
    webhook_urls: List[str] = field(default_factory=list)
    
    # Monitoring settings
    metrics_retention_days: int = 30
    alert_retention_days: int = 90
    check_interval_seconds: int = 30
    enable_anomaly_detection: bool = True
    anomaly_sensitivity: float = 0.1
    
    # Prometheus settings
    prometheus_port: int = 8000
    prometheus_enabled: bool = True
    
    # Database settings
    database_path: str = "monitoring.db"
    
    # System resource monitoring
    cpu_threshold: float = 80.0
    memory_threshold: float = 80.0
    disk_threshold: float = 90.0
    
    # Pipeline specific
    pipeline_error_threshold: float = 5.0  # percentage
    pipeline_latency_threshold: float = 300.0  # seconds
    data_quality_threshold: float = 95.0  # percentage


class AlertManager:
    """Manages alert delivery and notifications"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alert_history: List[Alert] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_suppressions: Set[str] = set()
        
    async def send_alert(self, alert: Alert):
        """Send alert through configured channels"""
        if alert.metric_name in self.alert_suppressions:
            logger.debug(f"Alert suppressed for metric: {alert.metric_name}")
            return
        
        # Add to active alerts
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)
        
        # Send to configured channels
        await self._send_to_slack(alert)
        await self._send_to_email(alert)
        await self._send_to_webhooks(alert)
        
        logger.info(f"Alert sent: {alert.title} ({alert.alert_level.value})")
    
    async def _send_to_slack(self, alert: Alert):
        """Send alert to Slack"""
        if not self.config.slack_webhook_url:
            return
        
        try:
            # Format Slack message
            color = {
                AlertLevel.INFO: "good",
                AlertLevel.WARNING: "warning", 
                AlertLevel.CRITICAL: "danger",
                AlertLevel.EMERGENCY: "danger"
            }.get(alert.alert_level, "warning")
            
            message = {
                "text": f"Pipeline Alert: {alert.title}",
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.alert_level.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Metric",
                                "value": alert.metric_name,
                                "short": True
                            },
                            {
                                "title": "Current Value",
                                "value": str(alert.current_value),
                                "short": True
                            },
                            {
                                "title": "Threshold",
                                "value": str(alert.threshold_value),
                                "short": True
                            },
                            {
                                "title": "Description",
                                "value": alert.description,
                                "short": False
                            },
                            {
                                "title": "Timestamp",
                                "value": alert.timestamp.isoformat(),
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.slack_webhook_url,
                    json=message
                ) as response:
                    if response.status == 200:
                        logger.debug("Alert sent to Slack successfully")
                    else:
                        logger.error(f"Failed to send alert to Slack: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error sending alert to Slack: {e}")
    
    async def _send_to_email(self, alert: Alert):
        """Send alert via email"""
        if not all([self.config.email_smtp_server, self.config.email_username, 
                   self.config.email_password, self.config.email_recipients]):
            return
        
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.config.email_username
            msg['To'] = ', '.join(self.config.email_recipients)
            msg['Subject'] = f"Pipeline Alert: {alert.title}"
            
            # Email body
            body = f"""
            Data Pipeline Alert
            
            Severity: {alert.alert_level.value.upper()}
            Metric: {alert.metric_name}
            Current Value: {alert.current_value}
            Threshold: {alert.threshold_value}
            
            Description:
            {alert.description}
            
            Timestamp: {alert.timestamp.isoformat()}
            
            Alert ID: {alert.alert_id}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.config.email_smtp_server, self.config.email_smtp_port)
            server.starttls()
            server.login(self.config.email_username, self.config.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.debug("Alert sent via email successfully")
            
        except Exception as e:
            logger.error(f"Error sending alert via email: {e}")
    
    async def _send_to_webhooks(self, alert: Alert):
        """Send alert to configured webhooks"""
        if not self.config.webhook_urls:
            return
        
        try:
            # Format webhook payload
            payload = {
                "alert_id": alert.alert_id,
                "level": alert.alert_level.value,
                "title": alert.title,
                "description": alert.description,
                "metric_name": alert.metric_name,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata
            }
            
            async with aiohttp.ClientSession() as session:
                for webhook_url in self.config.webhook_urls:
                    try:
                        async with session.post(
                            webhook_url,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                logger.debug(f"Alert sent to webhook {webhook_url}")
                            else:
                                logger.error(f"Failed to send alert to webhook {webhook_url}: {response.status}")
                    except Exception as e:
                        logger.error(f"Error sending alert to webhook {webhook_url}: {e}")
                        
        except Exception as e:
            logger.error(f"Error sending alerts to webhooks: {e}")
    
    def resolve_alert(self, alert_id: str):
        """Resolve an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert resolved: {alert.title}")
    
    def suppress_alert(self, metric_name: str):
        """Suppress alerts for a specific metric"""
        self.alert_suppressions.add(metric_name)
        logger.info(f"Alerts suppressed for metric: {metric_name}")
    
    def unsuppress_alert(self, metric_name: str):
        """Remove alert suppression for a specific metric"""
        self.alert_suppressions.discard(metric_name)
        logger.info(f"Alert suppression removed for metric: {metric_name}")


class MetricsCollector:
    """Collects and stores metrics from various sources"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.metrics_by_name: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Prometheus metrics
        if config.prometheus_enabled:
            self.prometheus_counters = {}
            self.prometheus_gauges = {}
            self.prometheus_histograms = {}
            
            # Start Prometheus server
            start_http_server(config.prometheus_port)
            logger.info(f"Prometheus metrics server started on port {config.prometheus_port}")
    
    def record_metric(self, metric: Metric):
        """Record a metric"""
        # Add to buffer
        self.metrics_buffer.append(metric)
        self.metrics_by_name[metric.name].append(metric)
        
        # Update Prometheus metrics
        if self.config.prometheus_enabled:
            self._update_prometheus_metric(metric)
        
        logger.debug(f"Recorded metric: {metric.name} = {metric.value}")
    
    def _update_prometheus_metric(self, metric: Metric):
        """Update Prometheus metrics"""
        try:
            if metric.metric_type == MetricType.COUNTER:
                if metric.name not in self.prometheus_counters:
                    self.prometheus_counters[metric.name] = Counter(
                        metric.name.replace('-', '_'), 
                        metric.description,
                        list(metric.tags.keys())
                    )
                self.prometheus_counters[metric.name].labels(**metric.tags).inc(metric.value)
            
            elif metric.metric_type == MetricType.GAUGE:
                if metric.name not in self.prometheus_gauges:
                    self.prometheus_gauges[metric.name] = Gauge(
                        metric.name.replace('-', '_'), 
                        metric.description,
                        list(metric.tags.keys())
                    )
                self.prometheus_gauges[metric.name].labels(**metric.tags).set(metric.value)
            
            elif metric.metric_type == MetricType.HISTOGRAM:
                if metric.name not in self.prometheus_histograms:
                    self.prometheus_histograms[metric.name] = Histogram(
                        metric.name.replace('-', '_'), 
                        metric.description,
                        list(metric.tags.keys())
                    )
                self.prometheus_histograms[metric.name].labels(**metric.tags).observe(metric.value)
                
        except Exception as e:
            logger.error(f"Error updating Prometheus metric: {e}")
    
    def get_recent_metrics(self, metric_name: str, minutes: int = 5) -> List[Metric]:
        """Get recent metrics for a given name"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        if metric_name not in self.metrics_by_name:
            return []
        
        return [
            metric for metric in self.metrics_by_name[metric_name]
            if metric.timestamp >= cutoff_time
        ]
    
    def get_metric_statistics(self, metric_name: str, minutes: int = 5) -> Dict[str, float]:
        """Get statistics for a metric"""
        recent_metrics = self.get_recent_metrics(metric_name, minutes)
        
        if not recent_metrics:
            return {}
        
        values = [m.value for m in recent_metrics]
        
        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'latest': values[-1] if values else 0
        }


class AnomalyDetector:
    """Detects anomalies in metrics using machine learning"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.models: Dict[str, IsolationForest] = {}
        self.training_data: Dict[str, List[float]] = defaultdict(list)
        self.model_path = Path("models/anomaly_detection")
        self.model_path.mkdir(parents=True, exist_ok=True)
    
    def train_model(self, metric_name: str, historical_data: List[float]):
        """Train anomaly detection model for a metric"""
        if len(historical_data) < 50:
            logger.warning(f"Insufficient data to train anomaly model for {metric_name}")
            return
        
        try:
            # Prepare data
            X = np.array(historical_data).reshape(-1, 1)
            
            # Train Isolation Forest model
            model = IsolationForest(
                contamination=self.config.anomaly_sensitivity,
                random_state=42
            )
            model.fit(X)
            
            # Store model
            self.models[metric_name] = model
            
            # Save model to disk
            model_file = self.model_path / f"{metric_name}.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model, f)
            
            logger.info(f"Trained anomaly detection model for {metric_name}")
            
        except Exception as e:
            logger.error(f"Error training anomaly model for {metric_name}: {e}")
    
    def detect_anomaly(self, metric_name: str, value: float) -> bool:
        """Detect if a metric value is anomalous"""
        if metric_name not in self.models:
            return False
        
        try:
            model = self.models[metric_name]
            prediction = model.predict([[value]])
            
            # -1 indicates anomaly, 1 indicates normal
            return prediction[0] == -1
            
        except Exception as e:
            logger.error(f"Error detecting anomaly for {metric_name}: {e}")
            return False
    
    def load_models(self):
        """Load pre-trained models from disk"""
        for model_file in self.model_path.glob("*.pkl"):
            try:
                metric_name = model_file.stem
                with open(model_file, 'rb') as f:
                    model = pickle.load(f)
                
                self.models[metric_name] = model
                logger.info(f"Loaded anomaly detection model for {metric_name}")
                
            except Exception as e:
                logger.error(f"Error loading model {model_file}: {e}")


class HealthChecker:
    """Checks overall system health"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.health_checks: Dict[str, Callable] = {}
        self.health_status = HealthStatus.HEALTHY
        self.last_check = datetime.now()
    
    def register_health_check(self, name: str, check_func: Callable):
        """Register a health check function"""
        self.health_checks[name] = check_func
        logger.info(f"Registered health check: {name}")
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_healthy = True
        
        for name, check_func in self.health_checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                results[name] = result
                
                if not result.get('healthy', False):
                    overall_healthy = False
                    
            except Exception as e:
                logger.error(f"Health check '{name}' failed: {e}")
                results[name] = {
                    'healthy': False,
                    'error': str(e)
                }
                overall_healthy = False
        
        # Update overall health status
        if overall_healthy:
            self.health_status = HealthStatus.HEALTHY
        else:
            # Determine severity based on failed checks
            critical_failures = sum(1 for r in results.values() if not r.get('healthy', False))
            if critical_failures >= len(self.health_checks) * 0.5:
                self.health_status = HealthStatus.CRITICAL
            else:
                self.health_status = HealthStatus.DEGRADED
        
        self.last_check = datetime.now()
        
        return {
            'overall_status': self.health_status.value,
            'last_check': self.last_check.isoformat(),
            'checks': results
        }


class ComprehensiveMonitoringSystem:
    """
    Comprehensive monitoring system for data pipelines
    Provides real-time monitoring, alerting, and health checks
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.metrics_collector = MetricsCollector(config)
        self.alert_manager = AlertManager(config)
        self.anomaly_detector = AnomalyDetector(config)
        self.health_checker = HealthChecker(config)
        
        # Thresholds and SLAs
        self.thresholds: Dict[str, Threshold] = {}
        self.slas: Dict[str, SLA] = {}
        
        # Database connection
        self.db_conn = None
        
        # Monitoring control
        self.is_running = False
        self.stop_event = threading.Event()
        self.monitor_thread = None
        
        # Initialize database
        self._initialize_database()
        
        # Load models
        self.anomaly_detector.load_models()
        
        # Register default health checks
        self._register_default_health_checks()
    
    def _initialize_database(self):
        """Initialize SQLite database for storing metrics and alerts"""
        try:
            self.db_conn = sqlite3.connect(self.config.database_path, check_same_thread=False)
            
            # Create tables
            self.db_conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    metric_type TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    tags TEXT,
                    description TEXT
                )
            ''')
            
            self.db_conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    alert_level TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    metric_name TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    threshold_value REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at DATETIME,
                    metadata TEXT
                )
            ''')
            
            # Create indexes
            self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp ON metrics(name, timestamp)')
            self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
            
            self.db_conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def _register_default_health_checks(self):
        """Register default system health checks"""
        
        def check_system_resources():
            """Check CPU, memory, and disk usage"""
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            healthy = (cpu_percent < self.config.cpu_threshold and 
                      memory_percent < self.config.memory_threshold and 
                      disk_percent < self.config.disk_threshold)
            
            return {
                'healthy': healthy,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'details': f"CPU: {cpu_percent:.1f}%, Memory: {memory_percent:.1f}%, Disk: {disk_percent:.1f}%"
            }
        
        def check_database_connection():
            """Check database connection"""
            try:
                if self.db_conn:
                    self.db_conn.execute('SELECT 1')
                    return {'healthy': True, 'details': 'Database connection OK'}
                else:
                    return {'healthy': False, 'details': 'Database connection not initialized'}
            except Exception as e:
                return {'healthy': False, 'details': f'Database connection error: {e}'}
        
        self.health_checker.register_health_check('system_resources', check_system_resources)
        self.health_checker.register_health_check('database_connection', check_database_connection)
    
    def add_threshold(self, threshold: Threshold):
        """Add a monitoring threshold"""
        self.thresholds[threshold.metric_name] = threshold
        logger.info(f"Added threshold for {threshold.metric_name}: "
                   f"warning={threshold.warning_threshold}, critical={threshold.critical_threshold}")
    
    def add_sla(self, sla: SLA):
        """Add an SLA configuration"""
        self.slas[sla.name] = sla
        logger.info(f"Added SLA: {sla.name} ({sla.target_percentage}%)")
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, 
                     tags: Optional[Dict[str, str]] = None, description: str = ""):
        """Record a metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            tags=tags or {},
            description=description
        )
        
        # Store in collector
        self.metrics_collector.record_metric(metric)
        
        # Store in database
        self._store_metric_in_db(metric)
        
        # Check for anomalies
        if self.config.enable_anomaly_detection:
            if self.anomaly_detector.detect_anomaly(name, value):
                self._create_anomaly_alert(metric)
        
        # Check thresholds
        self._check_thresholds(metric)
    
    def _store_metric_in_db(self, metric: Metric):
        """Store metric in database"""
        try:
            self.db_conn.execute('''
                INSERT INTO metrics (name, value, metric_type, timestamp, tags, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                metric.name,
                metric.value,
                metric.metric_type.value,
                metric.timestamp,
                json.dumps(metric.tags),
                metric.description
            ))
            
            self.db_conn.commit()
            
        except Exception as e:
            logger.error(f"Error storing metric in database: {e}")
    
    def _check_thresholds(self, metric: Metric):
        """Check if metric violates any thresholds"""
        if metric.name not in self.thresholds:
            return
        
        threshold = self.thresholds[metric.name]
        if not threshold.enabled:
            return
        
        # Evaluate threshold
        violated = False
        alert_level = None
        
        if threshold.comparison_operator == ">":
            if metric.value > threshold.critical_threshold:
                violated = True
                alert_level = AlertLevel.CRITICAL
            elif metric.value > threshold.warning_threshold:
                violated = True
                alert_level = AlertLevel.WARNING
        elif threshold.comparison_operator == "<":
            if metric.value < threshold.critical_threshold:
                violated = True
                alert_level = AlertLevel.CRITICAL
            elif metric.value < threshold.warning_threshold:
                violated = True
                alert_level = AlertLevel.WARNING
        # Add more operators as needed
        
        if violated:
            self._create_threshold_alert(metric, threshold, alert_level)
    
    def _create_threshold_alert(self, metric: Metric, threshold: Threshold, alert_level: AlertLevel):
        """Create an alert for threshold violation"""
        alert = Alert(
            alert_id=f"{metric.name}_{threshold.comparison_operator}_{threshold.critical_threshold}_{int(time.time())}",
            alert_level=alert_level,
            title=f"Threshold Violation: {metric.name}",
            description=f"Metric {metric.name} value {metric.value} violates {alert_level.value} threshold {threshold.critical_threshold if alert_level == AlertLevel.CRITICAL else threshold.warning_threshold}",
            metric_name=metric.name,
            current_value=metric.value,
            threshold_value=threshold.critical_threshold if alert_level == AlertLevel.CRITICAL else threshold.warning_threshold,
            timestamp=datetime.now(),
            metadata={'threshold_config': threshold.__dict__}
        )
        
        # Send alert
        asyncio.create_task(self.alert_manager.send_alert(alert))
        
        # Store in database
        self._store_alert_in_db(alert)
    
    def _create_anomaly_alert(self, metric: Metric):
        """Create an alert for anomaly detection"""
        alert = Alert(
            alert_id=f"anomaly_{metric.name}_{int(time.time())}",
            alert_level=AlertLevel.WARNING,
            title=f"Anomaly Detected: {metric.name}",
            description=f"Metric {metric.name} value {metric.value} is anomalous based on historical patterns",
            metric_name=metric.name,
            current_value=metric.value,
            threshold_value=0.0,  # Not applicable for anomaly detection
            timestamp=datetime.now(),
            metadata={'anomaly_detection': True}
        )
        
        # Send alert
        asyncio.create_task(self.alert_manager.send_alert(alert))
        
        # Store in database
        self._store_alert_in_db(alert)
    
    def _store_alert_in_db(self, alert: Alert):
        """Store alert in database"""
        try:
            self.db_conn.execute('''
                INSERT INTO alerts (alert_id, alert_level, title, description, metric_name, 
                                  current_value, threshold_value, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id,
                alert.alert_level.value,
                alert.title,
                alert.description,
                alert.metric_name,
                alert.current_value,
                alert.threshold_value,
                alert.timestamp,
                json.dumps(alert.metadata)
            ))
            
            self.db_conn.commit()
            
        except Exception as e:
            logger.error(f"Error storing alert in database: {e}")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self.stop_event.is_set():
            try:
                # Run health checks
                asyncio.run(self.health_checker.run_health_checks())
                
                # Record system metrics
                self.record_metric(
                    'system_cpu_percent',
                    psutil.cpu_percent(),
                    MetricType.GAUGE,
                    description="System CPU usage percentage"
                )
                
                self.record_metric(
                    'system_memory_percent',
                    psutil.virtual_memory().percent,
                    MetricType.GAUGE,
                    description="System memory usage percentage"
                )
                
                self.record_metric(
                    'system_disk_percent',
                    psutil.disk_usage('/').percent,
                    MetricType.GAUGE,
                    description="System disk usage percentage"
                )
                
                # Sleep until next check
                self.stop_event.wait(self.config.check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                logger.error(traceback.format_exc())
                time.sleep(60)  # Wait before retrying
    
    def start(self):
        """Start the monitoring system"""
        if self.is_running:
            logger.warning("Monitoring system is already running")
            return
        
        logger.info("Starting monitoring system")
        self.is_running = True
        self.stop_event.clear()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="MonitoringLoop",
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info("Monitoring system started")
    
    def stop(self):
        """Stop the monitoring system"""
        if not self.is_running:
            logger.warning("Monitoring system is not running")
            return
        
        logger.info("Stopping monitoring system")
        self.is_running = False
        self.stop_event.set()
        
        # Wait for thread to finish
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        # Close database connection
        if self.db_conn:
            self.db_conn.close()
        
        logger.info("Monitoring system stopped")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        try:
            # Get recent metrics
            cursor = self.db_conn.execute('''
                SELECT name, AVG(value) as avg_value, COUNT(*) as count
                FROM metrics 
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY name
                ORDER BY name
            ''')
            
            metrics_summary = {row[0]: {'avg': row[1], 'count': row[2]} for row in cursor.fetchall()}
            
            # Get recent alerts
            cursor = self.db_conn.execute('''
                SELECT alert_level, COUNT(*) as count
                FROM alerts 
                WHERE timestamp > datetime('now', '-24 hours')
                GROUP BY alert_level
            ''')
            
            alerts_summary = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get health status
            health_status = asyncio.run(self.health_checker.run_health_checks())
            
            return {
                'timestamp': datetime.now().isoformat(),
                'health_status': health_status,
                'metrics_summary': metrics_summary,
                'alerts_summary': alerts_summary,
                'active_alerts': len(self.alert_manager.active_alerts),
                'total_metrics': len(self.metrics_collector.metrics_buffer)
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {'error': str(e)}


# Example usage
async def main():
    """Example usage of the monitoring system"""
    
    # Create configuration
    config = MonitoringConfig(
        slack_webhook_url=os.getenv('SLACK_WEBHOOK_URL'),
        email_recipients=['admin@example.com'],
        prometheus_enabled=True,
        enable_anomaly_detection=True
    )
    
    # Create monitoring system
    monitor = ComprehensiveMonitoringSystem(config)
    
    # Add some thresholds
    monitor.add_threshold(Threshold(
        metric_name='pipeline_error_rate',
        warning_threshold=5.0,
        critical_threshold=10.0,
        comparison_operator='>'
    ))
    
    monitor.add_threshold(Threshold(
        metric_name='system_cpu_percent',
        warning_threshold=80.0,
        critical_threshold=90.0,
        comparison_operator='>'
    ))
    
    try:
        # Start monitoring
        monitor.start()
        
        # Simulate some metrics
        for i in range(100):
            monitor.record_metric(
                'pipeline_items_processed',
                i * 10,
                MetricType.COUNTER,
                {'pipeline': 'test'}
            )
            
            monitor.record_metric(
                'pipeline_error_rate',
                i * 0.1,
                MetricType.GAUGE,
                {'pipeline': 'test'}
            )
            
            await asyncio.sleep(1)
        
        # Get dashboard data
        dashboard = monitor.get_dashboard_data()
        print(f"Dashboard data: {json.dumps(dashboard, indent=2)}")
        
    finally:
        monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())