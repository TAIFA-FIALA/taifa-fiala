# TAIFA Source Validation Module

## Overview

The Source Validation Module is a comprehensive system for validating, integrating, and monitoring external funding sources submitted by community members and institutional partners. It implements a multi-stage workflow from initial submission to production integration with continuous performance monitoring.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Source        │    │    Validation    │    │   Classification│
│   Submission    │───▶│    & Quality     │───▶│   & Technical   │
│                 │    │    Assessment    │    │   Assessment    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Manual        │    │     Pilot        │    │   Performance   │
│   Review        │◀───│   Monitoring     │───▶│   Evaluation    │
│   (if needed)   │    │   (30 days)      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Production     │    │   Ongoing       │
                       │   Integration    │───▶│   Monitoring    │
                       │                  │    │                 │
                       └──────────────────┘    └─────────────────┘
```

## Components

### 1. SourceValidator
Validates submitted sources against quality, accessibility, and authority criteria.

**Key Features:**
- URL accessibility checking
- Content relevance assessment (AI/Africa/Funding)
- Authority verification (email domain matching)
- robots.txt compliance checking
- Sample URL quality validation

### 2. DeduplicationPipeline
Multi-layer deduplication system to prevent duplicate opportunities.

**Deduplication Layers:**
- **URL-based**: Exact and similar URL matching
- **Content-based**: Hash comparison and semantic similarity
- **Metadata-based**: Organization + amount + deadline combinations

### 3. SourceClassifier
Classifies sources by type and determines optimal monitoring strategies.

**Supported Source Types:**
- RSS Feeds (highest reliability)
- APIs (high reliability, may need auth)
- Email Newsletters (medium reliability)
- Static Web Pages (medium reliability)
- Dynamic Web Pages (lower reliability, requires headless browsing)
- PDF Publications (low frequency)
- Social Media (requires API access)

### 4. PerformanceTracker
Monitors and evaluates source performance during pilot and production phases.

**Tracked Metrics:**
- Volume: opportunities discovered, relevance rates
- Quality: community approval, duplicate rates, data completeness
- Technical: monitoring reliability, error rates, response times
- Value: unique opportunities, high-value opportunities, success rates

### 5. SourceValidationOrchestrator
Main orchestrator that coordinates the entire workflow.

**Key Workflows:**
- Source submission processing
- Manual review management
- Pilot monitoring oversight
- Production integration decisions

## Database Schema

The module requires several new database tables:

- `source_submissions` - All submitted sources
- `manual_review_queue` - Sources requiring human review
- `pilot_monitoring` - 30-day pilot tracking
- `source_performance_metrics` - Performance evaluations
- `deduplication_logs` - Duplicate detection results
- `source_monitoring_logs` - Technical monitoring logs
- `application_outcomes` - Success tracking

## API Endpoints

### Public Endpoints
- `GET /source-validation/submit-form` - Get form configuration
- `POST /source-validation/submit` - Submit new source

### Monitoring Endpoints
- `GET /source-validation/submissions` - List submissions
- `GET /source-validation/submissions/{id}` - Get submission status
- `GET /source-validation/pilots/dashboard` - Pilot monitoring dashboard

### Admin Endpoints
- `GET /source-validation/manual-review/queue` - Review queue
- `POST /source-validation/manual-review/{id}/decision` - Process review
- `POST /source-validation/pilots/{id}/evaluate` - Evaluate pilot
- `GET /source-validation/analytics` - Performance analytics

### Deduplication
- `POST /source-validation/deduplication/check` - Check for duplicates

## Installation & Setup

### 1. Database Setup
```bash
# Run the schema migration
psql -d your_database -f backend/app/services/source_validation/schema.sql
```

### 2. Dependencies
Add to `requirements.txt`:
```
sentence-transformers>=2.2.0
fuzzywuzzy>=0.18.0
python-levenshtein>=0.20.0
feedparser>=6.0.0
beautifulsoup4>=4.11.0
aiohttp>=3.8.0
playwright>=1.30.0  # For dynamic web scraping
```

### 3. Configuration
Add to environment variables:
```bash
# Translation APIs (optional)
AZURE_TRANSLATOR_KEY=your_key
GOOGLE_TRANSLATE_KEY=your_key
DEEPL_API_KEY=your_key

# Monitoring settings
SOURCE_VALIDATION_PILOT_DURATION=30  # days
PERFORMANCE_EVALUATION_FREQUENCY=30  # days
```

## Usage Examples

### 1. Submit a Source Programmatically
```python
from app.services.source_validation import SourceValidationOrchestrator, SourceSubmission
from datetime import datetime

submission = SourceSubmission(
    name="University Research Office",
    url="https://university.edu/research/funding",
    contact_person="Dr. Jane Smith",
    contact_email="jane.smith@university.edu",
    source_type="webpage",
    update_frequency="monthly",
    geographic_focus=["Kenya", "East Africa"],
    expected_volume="5-20",
    sample_urls=["https://university.edu/research/funding/ai-grant"],
    ai_relevance_estimate=80,
    africa_relevance_estimate=90,
    language="English",
    submitter_role="Research Funding Manager",
    has_permission=True,
    preferred_contact="email",
    submitted_at=datetime.now()
)

async with SourceValidationOrchestrator() as orchestrator:
    result = await orchestrator.submit_source(submission)
    print(f"Submission ID: {result.submission_id}")
    print(f"Status: {result.status.value}")
```

### 2. Check for Duplicates
```python
from app.services.source_validation import DeduplicationPipeline, OpportunityContent

opportunity = OpportunityContent(
    url="https://example.org/grant-2025",
    title="AI Research Grant",
    description="Funding for AI research in healthcare",
    organization="Example Foundation",
    amount=50000.0,
    currency="USD"
)

pipeline = DeduplicationPipeline()
result = await pipeline.check_for_duplicates(opportunity)

if result["is_duplicate"]:
    print(f"Duplicate found: {result['primary_match_type']}")
    print(f"Existing opportunity: {result['existing_opportunity_id']}")
```

### 3. Evaluate Source Performance
```python
from app.services.source_validation import PerformanceTracker

tracker = PerformanceTracker()
metrics = await tracker.evaluate_source_performance(source_id=123, evaluation_days=30)

print(f"Overall Score: {metrics.overall_score:.2f}")
print(f"Status: {metrics.performance_status.value}")
print(f"Approval Rate: {metrics.community_approval_rate:.1%}")
print(f"Duplicate Rate: {metrics.duplicate_rate:.1%}")
```

## Integration with Existing TAIFA Systems

### 1. CrewAI ETL Pipeline
The source validation module integrates with your CrewAI agents:

```python
# In your CrewAI processing
from app.services.source_validation import DeduplicationPipeline

async def process_opportunity(raw_opportunity):
    # First check for duplicates
    dedup_pipeline = DeduplicationPipeline()
    dedup_result = await dedup_pipeline.check_for_duplicates(raw_opportunity)
    
    if dedup_result["is_duplicate"]:
        # Skip CrewAI processing and community validation
        return {"status": "duplicate", "existing_id": dedup_result["existing_opportunity_id"]}
    
    # Proceed with CrewAI agent processing
    processed = await crewai_agents.process(raw_opportunity)
    return processed
```

### 2. Community Validation
Only unique opportunities reach community validation:

```python
# Before community validation
if opportunity_confidence < 0.9:
    # Check duplicates first
    dedup_result = await check_duplicates(opportunity)
    if not dedup_result["is_duplicate"]:
        # Send to community validation
        await queue_for_community_validation(opportunity)
```

### 3. Translation Pipeline
Sources can be validated in multiple languages:

```python
# Multi-language source support
if submission.language == "French":
    # Use French-specific validation criteria
    # Integrate with translation pipeline for community validation
```

## Performance Thresholds

### Minimum Requirements for Production
- **AI Relevance**: ≥30% of content must be AI-related
- **Africa Relevance**: ≥50% must apply to African organizations
- **Community Approval**: ≥70% approval rate
- **Duplicate Rate**: ≤20% duplicates
- **Monitoring Reliability**: ≥95% uptime

### Preferred Performance
- **Unique Opportunities**: ≥5 per month
- **High-Value Opportunities**: ≥1 per month (>$10K)
- **Data Completeness**: ≥80% complete records

## Monitoring and Alerts

### Automated Monitoring
- Daily health checks for all active sources
- Performance evaluation every 30 days
- Automatic alerts for failing sources

### Dashboard Metrics
- Total submissions and status breakdown
- Pilot performance overview
- Source reliability metrics
- Deduplication effectiveness

## Troubleshooting

### Common Issues

1. **High Duplicate Rate**
   - Review source overlap with existing sources
   - Adjust deduplication thresholds
   - Check for content syndication

2. **Low Community Approval**
   - Review content relevance criteria
   - Improve content filtering
   - Analyze rejected opportunities

3. **Technical Reliability Issues**
   - Check robots.txt compliance
   - Review rate limiting settings
   - Monitor source website changes

### Debugging Tools

```python
# Enable debug logging
import logging
logging.getLogger('app.services.source_validation').setLevel(logging.DEBUG)

# Test individual components
async def debug_source_validation():
    async with SourceValidator() as validator:
        result = await validator.validate_submission(test_submission)
        print("Validation checks:", result.checks)
```

## Contributing

When adding new features to the source validation module:

1. Update the appropriate component class
2. Add database migrations if needed
3. Update API endpoints as necessary
4. Add comprehensive tests
5. Update this documentation

## Security Considerations

- Source submissions are validated for malicious content
- Rate limiting prevents spam submissions
- Email domain verification reduces false submissions
- Manual review queue for uncertain cases
- Audit logging for all validation decisions

This module provides a robust foundation for community-driven source discovery while maintaining high quality standards for the TAIFA platform.
