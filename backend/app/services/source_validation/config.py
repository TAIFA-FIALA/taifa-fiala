"""
Source Validation Configuration

Configuration management for source validation thresholds, settings, and feature flags.
Supports environment variables, database configuration, and runtime updates.
"""

import os
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging

from app.core.database import get_database


logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Notification channels for source validation events"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    DISCORD = "discord"


@dataclass
class ValidationThresholds:
    """Validation score thresholds for different decisions"""
    # Automatic approval threshold
    auto_approve_threshold: float = 0.8
    
    # Manual review threshold
    manual_review_threshold: float = 0.6
    
    # Automatic rejection threshold (below this = reject)
    auto_reject_threshold: float = 0.4
    
    # Minimum requirements for pilot approval
    min_ai_relevance: float = 0.30
    min_africa_relevance: float = 0.50
    min_community_approval: float = 0.70
    max_duplicate_rate: float = 0.20
    min_monitoring_reliability: float = 0.95
    
    # Preferred performance levels
    preferred_unique_opportunities: int = 5  # per month
    preferred_high_value_count: int = 1     # per month
    preferred_completeness: float = 0.80
    
    # Failing thresholds (immediate action required)
    failing_approval_rate: float = 0.50
    failing_reliability: float = 0.80
    failing_duplicate_rate: float = 0.40


@dataclass
class PilotSettings:
    """Settings for pilot monitoring periods"""
    # Default pilot duration
    default_duration_days: int = 30
    
    # Maximum pilot extensions allowed
    max_extensions: int = 2
    
    # Extension duration
    extension_duration_days: int = 30
    
    # Minimum evaluation interval
    min_evaluation_interval_days: int = 7
    
    # Performance check frequency
    performance_check_frequency_hours: int = 24
    
    # Auto-evaluation after pilot end
    auto_evaluate_on_completion: bool = True


@dataclass
class MonitoringSettings:
    """Settings for source monitoring and data collection"""
    # Default monitoring frequencies by source type
    rss_feed_frequency_minutes: int = 15
    api_frequency_minutes: int = 120
    webpage_frequency_hours: int = 12
    newsletter_check_frequency_minutes: int = 60
    
    # Timeout settings
    default_timeout_seconds: int = 30
    long_timeout_seconds: int = 120
    
    # Retry settings
    default_retry_attempts: int = 3
    max_retry_attempts: int = 5
    retry_backoff_seconds: int = 60
    
    # Rate limiting
    requests_per_minute: int = 10
    requests_per_hour: int = 100
    
    # User agent string
    user_agent: str = "TAIFA-Bot/1.0 (AI Funding Tracker; +https://taifa-africa.com)"
    
    # Respect robots.txt
    respect_robots_txt: bool = True


@dataclass
class DeduplicationSettings:
    """Settings for deduplication pipeline"""
    # Similarity thresholds
    url_similarity_threshold: float = 0.8
    content_similarity_threshold: float = 0.9
    semantic_similarity_threshold: float = 0.9
    title_similarity_threshold: float = 0.85
    
    # Content hash settings
    enable_content_hashing: bool = True
    hash_algorithm: str = "sha256"
    
    # Semantic similarity settings
    enable_semantic_similarity: bool = True
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Metadata comparison settings
    amount_tolerance_percent: float = 0.1  # 10% tolerance
    deadline_tolerance_days: int = 7
    
    # Performance settings
    max_candidates_to_check: int = 100
    similarity_check_timeout_seconds: int = 30


@dataclass
class NotificationSettings:
    """Settings for notifications and alerts"""
    # Enabled notification channels
    enabled_channels: list = None
    
    # Email settings
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@taifa-africa.com"
    
    # Slack settings
    slack_webhook_url: str = ""
    slack_channel: str = "#taifa-alerts"
    
    # Webhook settings
    webhook_url: str = ""
    webhook_secret: str = ""
    
    # Discord settings
    discord_webhook_url: str = ""
    
    # Notification preferences
    notify_on_submission: bool = True
    notify_on_approval: bool = True
    notify_on_rejection: bool = True
    notify_on_pilot_completion: bool = True
    notify_on_production_integration: bool = True
    notify_on_source_failure: bool = True
    
    def __post_init__(self):
        if self.enabled_channels is None:
            self.enabled_channels = [NotificationChannel.EMAIL.value]


@dataclass
class PerformanceSettings:
    """Settings for performance evaluation and scoring"""
    # Evaluation frequency
    evaluation_frequency_days: int = 30
    
    # Score weights (must sum to 1.0)
    volume_weight: float = 0.25
    quality_weight: float = 0.35
    technical_weight: float = 0.25
    value_weight: float = 0.15
    
    # Minimum data requirements for evaluation
    min_opportunities_for_evaluation: int = 5
    min_monitoring_days: int = 7
    
    # Performance status thresholds
    excellent_threshold: float = 0.9
    good_threshold: float = 0.75
    acceptable_threshold: float = 0.6
    
    # Auto-actions based on performance
    auto_promote_excellent_pilots: bool = True
    auto_flag_poor_sources: bool = True
    auto_deprecate_failing_sources: bool = False  # Require manual confirmation


@dataclass
class SecuritySettings:
    """Security settings for source validation"""
    # URL validation
    allowed_schemes: list = None
    blocked_domains: list = None
    require_https: bool = False
    
    # Content validation
    max_content_length_mb: int = 10
    scan_for_malware: bool = False
    
    # Rate limiting for submissions
    max_submissions_per_ip_per_hour: int = 5
    max_submissions_per_email_per_day: int = 3
    
    # Manual review requirements
    require_manual_review_for_new_domains: bool = True
    require_manual_review_for_high_volume: bool = True
    
    def __post_init__(self):
        if self.allowed_schemes is None:
            self.allowed_schemes = ["http", "https"]
        if self.blocked_domains is None:
            self.blocked_domains = []


class SourceValidationConfig:
    """Main configuration class for source validation module"""
    
    def __init__(self):
        self._validation_thresholds = ValidationThresholds()
        self._pilot_settings = PilotSettings()
        self._monitoring_settings = MonitoringSettings()
        self._deduplication_settings = DeduplicationSettings()
        self._notification_settings = NotificationSettings()
        self._performance_settings = PerformanceSettings()
        self._security_settings = SecuritySettings()
        
        # Load configuration from environment and database
        self._load_from_environment()
    
    @property
    def validation_thresholds(self) -> ValidationThresholds:
        return self._validation_thresholds
    
    @property
    def pilot_settings(self) -> PilotSettings:
        return self._pilot_settings
    
    @property
    def monitoring_settings(self) -> MonitoringSettings:
        return self._monitoring_settings
    
    @property
    def deduplication_settings(self) -> DeduplicationSettings:
        return self._deduplication_settings
    
    @property
    def notification_settings(self) -> NotificationSettings:
        return self._notification_settings
    
    @property
    def performance_settings(self) -> PerformanceSettings:
        return self._performance_settings
    
    @property
    def security_settings(self) -> SecuritySettings:
        return self._security_settings
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        
        # Validation thresholds
        self._validation_thresholds.auto_approve_threshold = float(
            os.getenv('SV_AUTO_APPROVE_THRESHOLD', 
                     self._validation_thresholds.auto_approve_threshold)
        )
        self._validation_thresholds.min_ai_relevance = float(
            os.getenv('SV_MIN_AI_RELEVANCE', 
                     self._validation_thresholds.min_ai_relevance)
        )
        self._validation_thresholds.min_africa_relevance = float(
            os.getenv('SV_MIN_AFRICA_RELEVANCE', 
                     self._validation_thresholds.min_africa_relevance)
        )
        self._validation_thresholds.min_community_approval = float(
            os.getenv('SV_MIN_COMMUNITY_APPROVAL', 
                     self._validation_thresholds.min_community_approval)
        )
        
        # Pilot settings
        self._pilot_settings.default_duration_days = int(
            os.getenv('SV_PILOT_DURATION_DAYS', 
                     self._pilot_settings.default_duration_days)
        )
        self._pilot_settings.max_extensions = int(
            os.getenv('SV_PILOT_MAX_EXTENSIONS', 
                     self._pilot_settings.max_extensions)
        )
        
        # Monitoring settings
        self._monitoring_settings.default_timeout_seconds = int(
            os.getenv('SV_DEFAULT_TIMEOUT_SECONDS', 
                     self._monitoring_settings.default_timeout_seconds)
        )
        self._monitoring_settings.requests_per_hour = int(
            os.getenv('SV_REQUESTS_PER_HOUR', 
                     self._monitoring_settings.requests_per_hour)
        )
        self._monitoring_settings.user_agent = os.getenv(
            'SV_USER_AGENT', 
            self._monitoring_settings.user_agent
        )
        
        # Notification settings
        self._notification_settings.smtp_server = os.getenv('SV_SMTP_SERVER', '')
        self._notification_settings.smtp_username = os.getenv('SV_SMTP_USERNAME', '')
        self._notification_settings.smtp_password = os.getenv('SV_SMTP_PASSWORD', '')
        self._notification_settings.from_email = os.getenv(
            'SV_FROM_EMAIL', 
            self._notification_settings.from_email
        )
        self._notification_settings.slack_webhook_url = os.getenv('SV_SLACK_WEBHOOK_URL', '')
        self._notification_settings.discord_webhook_url = os.getenv('SV_DISCORD_WEBHOOK_URL', '')
        
        # Security settings
        self._security_settings.require_https = os.getenv('SV_REQUIRE_HTTPS', 'false').lower() == 'true'
        self._security_settings.max_submissions_per_ip_per_hour = int(
            os.getenv('SV_MAX_SUBMISSIONS_PER_IP_PER_HOUR', 
                     self._security_settings.max_submissions_per_ip_per_hour)
        )
    
    async def load_from_database(self):
        """Load configuration from database (overrides environment)"""
        try:
            db = await get_database()
            
            # Get all source validation configuration
            config_rows = await db.fetch_all(
                "SELECT key, value FROM configuration WHERE key LIKE 'source_validation.%'"
            )
            
            config_dict = {row['key']: row['value'] for row in config_rows}
            
            # Apply database configuration
            for key, value in config_dict.items():
                self._apply_database_config(key, value)
            
            logger.info(f"Loaded {len(config_dict)} configuration values from database")
            
        except Exception as e:
            logger.warning(f"Failed to load configuration from database: {e}")
    
    def _apply_database_config(self, key: str, value: str):
        """Apply a single configuration value from database"""
        try:
            # Parse the configuration key
            parts = key.split('.')
            if len(parts) < 2 or parts[0] != 'source_validation':
                return
            
            config_section = parts[1]
            config_key = '.'.join(parts[2:]) if len(parts) > 2 else ''
            
            # Convert string value to appropriate type
            parsed_value = self._parse_config_value(value)
            
            # Apply to appropriate configuration section
            if config_section == 'thresholds' and hasattr(self._validation_thresholds, config_key):
                setattr(self._validation_thresholds, config_key, parsed_value)
            elif config_section == 'pilot' and hasattr(self._pilot_settings, config_key):
                setattr(self._pilot_settings, config_key, parsed_value)
            elif config_section == 'monitoring' and hasattr(self._monitoring_settings, config_key):
                setattr(self._monitoring_settings, config_key, parsed_value)
            elif config_section == 'deduplication' and hasattr(self._deduplication_settings, config_key):
                setattr(self._deduplication_settings, config_key, parsed_value)
            elif config_section == 'performance' and hasattr(self._performance_settings, config_key):
                setattr(self._performance_settings, config_key, parsed_value)
            elif config_section == 'security' and hasattr(self._security_settings, config_key):
                setattr(self._security_settings, config_key, parsed_value)
            
        except Exception as e:
            logger.warning(f"Failed to apply database config {key}={value}: {e}")
    
    def _parse_config_value(self, value: str) -> Union[str, int, float, bool, list]:
        """Parse configuration value from string to appropriate type"""
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer
        try:
            if '.' not in value:
                return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Try JSON (for lists/objects)
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Return as string
        return value
    
    async def update_config(self, key: str, value: Any) -> bool:
        """Update configuration value in database"""
        try:
            db = await get_database()
            
            # Convert value to string for storage
            if isinstance(value, (dict, list)):
                str_value = json.dumps(value)
            else:
                str_value = str(value)
            
            # Update or insert configuration
            await db.execute(
                """
                INSERT INTO configuration (key, value, description, updated_at)
                VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                f"source_validation.{key}",
                str_value,
                f"Source validation setting: {key}"
            )
            
            # Apply the change to current configuration
            self._apply_database_config(f"source_validation.{key}", str_value)
            
            logger.info(f"Updated configuration: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration {key}: {e}")
            return False
    
    def get_monitoring_frequency(self, source_type: str) -> int:
        """Get monitoring frequency in minutes for source type"""
        frequencies = {
            'rss_feed': self._monitoring_settings.rss_feed_frequency_minutes,
            'api': self._monitoring_settings.api_frequency_minutes,
            'webpage': self._monitoring_settings.webpage_frequency_hours * 60,
            'newsletter': self._monitoring_settings.newsletter_check_frequency_minutes,
            'dynamic_webpage': self._monitoring_settings.webpage_frequency_hours * 60,
            'static_webpage': self._monitoring_settings.webpage_frequency_hours * 60
        }
        
        return frequencies.get(source_type, 720)  # Default: 12 hours
    
    def should_auto_approve(self, validation_score: float) -> bool:
        """Check if validation score qualifies for auto-approval"""
        return validation_score >= self._validation_thresholds.auto_approve_threshold
    
    def should_manual_review(self, validation_score: float) -> bool:
        """Check if validation score requires manual review"""
        return (self._validation_thresholds.auto_reject_threshold <= 
                validation_score < self._validation_thresholds.auto_approve_threshold)
    
    def should_auto_reject(self, validation_score: float) -> bool:
        """Check if validation score qualifies for auto-rejection"""
        return validation_score < self._validation_thresholds.auto_reject_threshold
    
    def is_notification_enabled(self, event_type: str) -> bool:
        """Check if notifications are enabled for event type"""
        notification_flags = {
            'submission': self._notification_settings.notify_on_submission,
            'approval': self._notification_settings.notify_on_approval,
            'rejection': self._notification_settings.notify_on_rejection,
            'pilot_completion': self._notification_settings.notify_on_pilot_completion,
            'production_integration': self._notification_settings.notify_on_production_integration,
            'source_failure': self._notification_settings.notify_on_source_failure
        }
        
        return notification_flags.get(event_type, False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'validation_thresholds': asdict(self._validation_thresholds),
            'pilot_settings': asdict(self._pilot_settings),
            'monitoring_settings': asdict(self._monitoring_settings),
            'deduplication_settings': asdict(self._deduplication_settings),
            'notification_settings': asdict(self._notification_settings),
            'performance_settings': asdict(self._performance_settings),
            'security_settings': asdict(self._security_settings)
        }


# Global configuration instance
_config_instance = None


def get_config() -> SourceValidationConfig:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = SourceValidationConfig()
    return _config_instance


async def reload_config():
    """Reload configuration from database"""
    config = get_config()
    await config.load_from_database()


# Configuration validation functions
def validate_config(config: SourceValidationConfig) -> list:
    """Validate configuration and return list of issues"""
    issues = []
    
    # Validate thresholds
    thresholds = config.validation_thresholds
    if thresholds.auto_approve_threshold <= thresholds.manual_review_threshold:
        issues.append("Auto-approve threshold must be higher than manual review threshold")
    
    if thresholds.manual_review_threshold <= thresholds.auto_reject_threshold:
        issues.append("Manual review threshold must be higher than auto-reject threshold")
    
    # Validate weights
    perf_settings = config.performance_settings
    total_weight = (perf_settings.volume_weight + perf_settings.quality_weight + 
                   perf_settings.technical_weight + perf_settings.value_weight)
    if abs(total_weight - 1.0) > 0.01:
        issues.append(f"Performance weights must sum to 1.0, got {total_weight}")
    
    # Validate notification settings
    notif_settings = config.notification_settings
    if NotificationChannel.EMAIL.value in notif_settings.enabled_channels:
        if not notif_settings.smtp_server:
            issues.append("SMTP server required for email notifications")
    
    if NotificationChannel.SLACK.value in notif_settings.enabled_channels:
        if not notif_settings.slack_webhook_url:
            issues.append("Slack webhook URL required for Slack notifications")
    
    return issues
