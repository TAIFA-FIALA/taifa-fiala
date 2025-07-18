# AI Africa Funding Tracker - Data Ingestion Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DATA INGESTION ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   MODULE 1  │  │   MODULE 2  │  │   MODULE 3  │  │   MODULE 4  │             │
│  │  RSS Feed   │  │    Serper   │  │    User     │  │   Crawl4AI  │             │
│  │   Ingestion │  │   Search    │  │ Submission  │  │  Extraction │             │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                 │                 │                 │                 │
│         │                 │                 │                 │                 │
│         └─────────────────┼─────────────────┼─────────────────┘                 │
│                           │                 │                                   │
│                           ▼                 ▼                                   │
│                  ┌─────────────────────────────────────────┐                    │ 
│                  │           INGESTION ROUTER              │                    │
│                  │       (Redis Queue Manager)             │                    │
│                  │     • Priority-based queuing            │                    │
│                  │     • Circuit breaker control           │                    │
│                  │     • Health monitoring                 │                    │
│                  └─────────────────────────────────────────┘                    │
│                                   │                                             │
│                                   ▼                                             │
│                  ┌─────────────────────────────────────────┐                    │
│                  │        CONTENT CLASSIFIER               │                    │
│                  │     • Opportunity vs Announcement       │                    │
│                  │     • Pattern matching + AI             │                    │
│                  │     • Source quality scoring            │                    │
│                  └─────────────────────────────────────────┘                    │
│                                   │                                             │
│                                   ▼                                             │
│                  ┌─────────────────────────────────────────┐                    │
│                  │      ENHANCED DUPLICATE DETECTOR        │                    │
│                  │     • 7 detection strategies            │                    │
│                  │     • Announcement chain detection      │                    │
│                  │     • Temporal clustering               │                    │
│                  │     • Organization-funding matching     │                    │
│                  └─────────────────────────────────────────┘                    │
│                                   │                                             │
│                                   ▼                                             │
│                  ┌─────────────────────────────────────────┐                    │
│                  │          AI VALIDATOR                   │                    │
│                  │     • Crawl4AI integration              │                    │
│                  │     • Quality scoring                   │                    │
│                  │     • Legitimacy assessment             │                    │
│                  └─────────────────────────────────────────┘                    │
│                                   │                                             │
│                          ┌────────┴────────┐                                    │
│                          ▼                 ▼                                    │
│                 ┌─────────────┐   ┌─────────────┐                               │
│                 │AUTO-APPROVE │   │   REVIEW    │                               │
│                 │   QUEUE     │   │   QUEUE     │                               │
│                 │ (>85% conf) │   │ (65-85%)    │                               │
│                 └─────────────┘   └─────────────┘                               │
│                          │                 │                                    │
│                          │                 ▼                                    │
│                          │        ┌─────────────┐                               │
│                          │        │  STREAMLIT  │                               │
│                          │        │   ADMIN     │                               │
│                          │        │ INTERFACE   │                               │
│                          │        └─────────────┘                               │
│                          │                 │                                    │
│                          └─────────────────┼─────────────────┐                  │
│                                           ▼                 ▼                   │
│                                  ┌─────────────────────────────────────────┐    │
│                                  │           DATABASE                      │    │
│                                  │        (Published)                      │    │
│                                  │   • Optimized indexes                   │    │
│                                  │   • Connection pooling                  │    │
│                                  │   • Caching layer                       │    │
│                                  └─────────────────────────────────────────┘    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Module Details

### Module 1: RSS Feed Ingestion
- **Location**: `backend/app/core/modules/rss_module.py`
- **Function**: Process RSS feeds with AI-powered content extraction
- **Rate Limit**: 200 requests/minute
- **Circuit Breaker**: 5 failures → open circuit
- **Health Monitoring**: Success rate, processing time, quality score

### Module 2: Serper Search
- **Location**: `backend/app/core/modules/serper_module.py`
- **Function**: Execute Serper API searches with relevance filtering
- **Rate Limit**: 100 requests/minute
- **Circuit Breaker**: 3 failures → open circuit
- **Health Monitoring**: API response time, result quality

### Module 3: User Submission
- **Location**: `backend/app/core/modules/user_submission_module.py`
- **Function**: Process user-submitted opportunities
- **Rate Limit**: 50 requests/minute
- **Circuit Breaker**: 2 failures → open circuit
- **Health Monitoring**: Validation success rate, user satisfaction

### Module 4: Crawl4AI Extraction
- **Location**: `backend/app/core/modules/crawl4ai_module.py`
- **Function**: Deep web content extraction using Crawl4AI
- **Rate Limit**: 30 requests/minute
- **Circuit Breaker**: 3 failures → open circuit
- **Health Monitoring**: Extraction success rate, content quality

## Data Flow Pipeline

### Stage 1: Ingestion (Parallel)
```python
# Each module runs independently
rss_results = await rss_module.ingest(rss_data)
serper_results = await serper_module.ingest(search_data)
user_results = await user_module.ingest(submission_data)
crawl_results = await crawl4ai_module.ingest(url_data)
```

### Stage 2: Content Classification
```python
# Filter out announcements vs opportunities
content_type = await classifier.classify_content(content)
if content_type == ContentType.FUNDING_ANNOUNCEMENT:
    reject_content()
```

### Stage 3: Duplicate Detection
```python
# 7 detection strategies
matches = await duplicate_detector.detect_duplicates(new_content, existing_content)
if matches:
    handle_duplicate(matches)
```

### Stage 4: AI Validation
```python
# Quality scoring and legitimacy check
validation_result = await ai_validator.validate(content)
if validation_result.confidence_score > 0.85:
    auto_approve()
elif validation_result.confidence_score > 0.65:
    send_to_review_queue()
else:
    reject()
```

## Circuit Breaker System

### Module Health States
- **ACTIVE**: Normal operation
- **DEGRADED**: Reduced performance but functional
- **FAILED**: Circuit breaker open, module disabled
- **MAINTENANCE**: Temporarily disabled for updates

### Failure Handling
```python
if module.circuit_breaker_failures >= threshold:
    module.circuit_breaker_open = True
    module.status = ModuleStatus.FAILED
    redirect_traffic_to_healthy_modules()
```

## Key Features for Data Quality

### 1. Content Type Classification
```python
# Patterns to identify funding announcements vs opportunities
announcement_patterns = [
    r'announces?\s+(funding|grant|investment)',
    r'(company|organization)\s+receives?\s+funding',
    r'funding\s+announcement'
]

opportunity_patterns = [
    r'apply\s+(for|to)',
    r'application\s+(deadline|due)',
    r'accepting\s+applications'
]
```

### 2. Enhanced Duplicate Detection
- **Exact signature matching**: Organization + Amount + Title hash
- **Title similarity**: 85% threshold with context
- **Content similarity**: TF-IDF + cosine similarity
- **Semantic similarity**: AI-powered comparison
- **Temporal clustering**: Same story within 72 hours
- **Organization-funding matching**: Same org, similar amounts
- **Announcement chain detection**: Multiple articles about same event

### 3. Source Quality Scoring
- Historical accuracy of source
- Duplicate rate from source
- Processing success rate
- Content relevance score

## Monitoring & Alerting

### Health Metrics
- **Success Rate**: Successful processing percentage
- **Processing Time**: Average time per item
- **Quality Score**: AI-assessed content quality
- **Duplicate Rate**: Percentage of duplicates detected

### Alerts
- Circuit breaker opened
- Quality score below threshold
- High duplicate rate from source
- Processing time exceeding limits

## Database Optimization

### Indexes
```sql
-- Full-text search
CREATE INDEX idx_opportunities_search ON funding_opportunities USING gin(search_vector);

-- Duplicate detection
CREATE INDEX idx_opportunities_title_hash ON funding_opportunities(title_hash);
CREATE INDEX idx_opportunities_org_amount ON funding_opportunities(organization_name, amount_usd);

-- Temporal queries
CREATE INDEX idx_opportunities_created_at ON funding_opportunities(created_at DESC);
```

### Connection Pooling
- **Pool Size**: 50 connections
- **Max Overflow**: 100 connections
- **Read Replicas**: Separate for queries
- **Connection Timeout**: 30 seconds

## Fault Isolation

### Module Independence
- Each module can fail without affecting others
- Circuit breakers prevent cascade failures
- Health monitoring enables proactive maintenance
- Graceful degradation maintains service availability

### Error Handling
```python
try:
    result = await module.process(data)
except ModuleException as e:
    logger.error(f"Module {module.name} failed: {e}")
    if module.circuit_breaker_failures >= threshold:
        disable_module(module)
    else:
        retry_with_backoff(module, data)
```

This architecture ensures high availability, data quality, and scalability while providing clear separation of concerns and fault isolation.