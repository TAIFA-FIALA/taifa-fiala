-- High-Volume Data Ingestion Schema
-- Optimized for 10K-100M records with fast inserts and queries

-- ==========================================
-- Raw Content Storage (Primary Ingestion)
-- ==========================================

-- Raw content table - optimized for massive inserts
CREATE TABLE IF NOT EXISTS raw_content (
    id BIGSERIAL PRIMARY KEY,
    
    -- Content fields
    title VARCHAR(1000),
    content TEXT,
    url VARCHAR(2000) NOT NULL,
    published_at TIMESTAMP,
    author VARCHAR(500),
    
    -- Source metadata
    source_name VARCHAR(200) NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'rss', 'news_api', 'web_scrape', 'api_integration'
    collected_at TIMESTAMP DEFAULT NOW(),
    keywords JSONB,
    
    -- Processing status
    processing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    processed_at TIMESTAMP,
    
    -- Content hash for deduplication
    content_hash VARCHAR(64) GENERATED ALWAYS AS (md5(url || title || content)) STORED,
    
    -- Metadata
    metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Unique constraint on URL to prevent duplicates
    CONSTRAINT unique_url UNIQUE (url)
);

-- ==========================================
-- Processed Content Storage
-- ==========================================

-- Processed content with AI analysis
CREATE TABLE IF NOT EXISTS processed_content (
    id BIGSERIAL PRIMARY KEY,
    raw_content_id BIGINT REFERENCES raw_content(id),
    
    -- AI Analysis Results
    funding_relevance_score FLOAT DEFAULT 0.0,
    ai_summary TEXT,
    ai_insights TEXT,
    extracted_entities JSONB,
    funding_signals JSONB,
    
    -- Classification
    content_category VARCHAR(100),
    funding_type VARCHAR(50), -- 'direct', 'indirect', 'potential'
    priority_score INTEGER DEFAULT 0,
    
    -- Processing metadata
    processing_model VARCHAR(100),
    processing_version VARCHAR(20),
    processing_duration_ms INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes for fast queries
    CONSTRAINT valid_relevance_score CHECK (funding_relevance_score >= 0 AND funding_relevance_score <= 1),
    CONSTRAINT valid_priority CHECK (priority_score >= 0 AND priority_score <= 100)
);

-- ==========================================
-- Batch Processing Tracking
-- ==========================================

-- Track batch processing jobs
CREATE TABLE IF NOT EXISTS batch_processing_jobs (
    id BIGSERIAL PRIMARY KEY,
    job_name VARCHAR(200) NOT NULL,
    job_type VARCHAR(50) NOT NULL, -- 'ingestion', 'processing', 'analysis'
    
    -- Job parameters
    source_filters JSONB,
    processing_params JSONB,
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Statistics
    total_items INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    
    -- Error tracking
    error_message TEXT,
    error_details JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- Data Source Management
-- ==========================================

-- Track data sources and their health
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    url VARCHAR(2000) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    
    -- Configuration
    check_interval_minutes INTEGER DEFAULT 60,
    priority VARCHAR(20) DEFAULT 'medium',
    keywords JSONB,
    headers JSONB,
    
    -- Status tracking
    enabled BOOLEAN DEFAULT TRUE,
    last_check TIMESTAMP,
    last_success TIMESTAMP,
    last_error TIMESTAMP,
    
    -- Statistics
    total_items_collected INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    -- Health metrics
    average_response_time_ms INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    
    -- Error tracking
    last_error_message TEXT,
    consecutive_errors INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_source_url UNIQUE (url)
);

-- ==========================================
-- Performance Optimization Tables
-- ==========================================

-- Content deduplication tracking
CREATE TABLE IF NOT EXISTS content_deduplication (
    id BIGSERIAL PRIMARY KEY,
    content_hash VARCHAR(64) NOT NULL,
    first_seen_id BIGINT REFERENCES raw_content(id),
    duplicate_count INTEGER DEFAULT 1,
    duplicate_urls JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_content_hash UNIQUE (content_hash)
);

-- Daily processing statistics
CREATE TABLE IF NOT EXISTS daily_processing_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    
    -- Ingestion stats
    total_items_ingested INTEGER DEFAULT 0,
    total_items_processed INTEGER DEFAULT 0,
    total_items_stored INTEGER DEFAULT 0,
    
    -- Source stats
    active_sources INTEGER DEFAULT 0,
    successful_sources INTEGER DEFAULT 0,
    failed_sources INTEGER DEFAULT 0,
    
    -- Processing stats
    average_processing_time_ms INTEGER DEFAULT 0,
    total_processing_time_ms BIGINT DEFAULT 0,
    
    -- Quality stats
    high_quality_items INTEGER DEFAULT 0,
    funding_relevant_items INTEGER DEFAULT 0,
    
    -- Error stats
    total_errors INTEGER DEFAULT 0,
    error_rate FLOAT DEFAULT 0.0,
    
    -- System stats
    peak_memory_mb INTEGER DEFAULT 0,
    peak_cpu_percent INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_date UNIQUE (date)
);

-- ==========================================
-- High-Performance Indexes
-- ==========================================

-- Raw content indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_raw_content_source_type ON raw_content(source_type);
CREATE INDEX IF NOT EXISTS idx_raw_content_collected_at ON raw_content(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_content_processing_status ON raw_content(processing_status);
CREATE INDEX IF NOT EXISTS idx_raw_content_published_at ON raw_content(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_content_source_name ON raw_content(source_name);
CREATE INDEX IF NOT EXISTS idx_raw_content_content_hash ON raw_content(content_hash);

-- Processed content indexes
CREATE INDEX IF NOT EXISTS idx_processed_content_raw_id ON processed_content(raw_content_id);
CREATE INDEX IF NOT EXISTS idx_processed_content_relevance ON processed_content(funding_relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_processed_content_priority ON processed_content(priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_processed_content_category ON processed_content(content_category);
CREATE INDEX IF NOT EXISTS idx_processed_content_funding_type ON processed_content(funding_type);

-- Data sources indexes
CREATE INDEX IF NOT EXISTS idx_data_sources_enabled ON data_sources(enabled);
CREATE INDEX IF NOT EXISTS idx_data_sources_last_check ON data_sources(last_check);
CREATE INDEX IF NOT EXISTS idx_data_sources_source_type ON data_sources(source_type);
CREATE INDEX IF NOT EXISTS idx_data_sources_priority ON data_sources(priority);

-- Batch processing indexes
CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON batch_processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_type ON batch_processing_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_created_at ON batch_processing_jobs(created_at DESC);

-- ==========================================
-- JSONB Indexes for Fast Queries
-- ==========================================

-- Raw content JSONB indexes
CREATE INDEX IF NOT EXISTS idx_raw_content_keywords_gin ON raw_content USING gin(keywords);
CREATE INDEX IF NOT EXISTS idx_raw_content_metadata_gin ON raw_content USING gin(metadata);

-- Processed content JSONB indexes
CREATE INDEX IF NOT EXISTS idx_processed_content_entities_gin ON processed_content USING gin(extracted_entities);
CREATE INDEX IF NOT EXISTS idx_processed_content_signals_gin ON processed_content USING gin(funding_signals);

-- Data sources JSONB indexes
CREATE INDEX IF NOT EXISTS idx_data_sources_keywords_gin ON data_sources USING gin(keywords);
CREATE INDEX IF NOT EXISTS idx_data_sources_headers_gin ON data_sources USING gin(headers);

-- ==========================================
-- Partitioning for Massive Scale
-- ==========================================

-- Partition raw_content by month for better performance
-- (This would be created programmatically for each month)

-- Example partitioning (would be done with a script)
-- CREATE TABLE raw_content_2024_01 PARTITION OF raw_content
-- FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- ==========================================
-- Functions for Maintenance
-- ==========================================

-- Function to cleanup old raw content
CREATE OR REPLACE FUNCTION cleanup_old_raw_content(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM raw_content 
    WHERE collected_at < NOW() - INTERVAL '1 day' * days_to_keep
    AND processing_status = 'completed';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup
    INSERT INTO daily_processing_stats (date, total_items_ingested)
    VALUES (CURRENT_DATE, -deleted_count)
    ON CONFLICT (date) DO UPDATE SET
        total_items_ingested = daily_processing_stats.total_items_ingested + EXCLUDED.total_items_ingested;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to update source health metrics
CREATE OR REPLACE FUNCTION update_source_health_metrics()
RETURNS VOID AS $$
BEGIN
    UPDATE data_sources SET
        success_rate = CASE 
            WHEN (success_count + error_count) > 0 
            THEN success_count::FLOAT / (success_count + error_count)
            ELSE 0.0
        END,
        updated_at = NOW()
    WHERE enabled = TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to get processing statistics
CREATE OR REPLACE FUNCTION get_processing_stats(days_back INTEGER DEFAULT 7)
RETURNS TABLE(
    date DATE,
    total_ingested INTEGER,
    total_processed INTEGER,
    processing_rate FLOAT,
    error_rate FLOAT,
    avg_quality_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dps.date,
        dps.total_items_ingested,
        dps.total_items_processed,
        CASE 
            WHEN dps.total_items_ingested > 0 
            THEN dps.total_items_processed::FLOAT / dps.total_items_ingested 
            ELSE 0.0 
        END as processing_rate,
        dps.error_rate,
        CASE 
            WHEN dps.total_items_processed > 0 
            THEN dps.high_quality_items::FLOAT / dps.total_items_processed 
            ELSE 0.0 
        END as avg_quality_score
    FROM daily_processing_stats dps
    WHERE dps.date >= CURRENT_DATE - INTERVAL '1 day' * days_back
    ORDER BY dps.date DESC;
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- Views for Common Queries
-- ==========================================

-- High-priority unprocessed content
CREATE VIEW unprocessed_priority_content AS
SELECT 
    rc.id,
    rc.title,
    rc.content,
    rc.url,
    rc.source_name,
    rc.collected_at,
    rc.keywords
FROM raw_content rc
WHERE rc.processing_status = 'pending'
  AND rc.collected_at >= NOW() - INTERVAL '7 days'
ORDER BY rc.collected_at DESC;

-- Source health dashboard
CREATE VIEW source_health_dashboard AS
SELECT 
    ds.name,
    ds.source_type,
    ds.enabled,
    ds.last_success,
    ds.last_error,
    ds.success_rate,
    ds.error_count,
    ds.consecutive_errors,
    CASE 
        WHEN ds.consecutive_errors > 5 THEN 'critical'
        WHEN ds.consecutive_errors > 2 THEN 'warning'
        WHEN ds.success_rate < 0.8 THEN 'degraded'
        ELSE 'healthy'
    END as health_status
FROM data_sources ds
WHERE ds.enabled = TRUE
ORDER BY ds.consecutive_errors DESC, ds.success_rate ASC;

-- Processing performance view
CREATE VIEW processing_performance AS
SELECT 
    DATE_TRUNC('hour', rc.collected_at) as hour,
    COUNT(*) as items_ingested,
    COUNT(pc.id) as items_processed,
    AVG(pc.funding_relevance_score) as avg_relevance_score,
    AVG(pc.processing_duration_ms) as avg_processing_time_ms
FROM raw_content rc
LEFT JOIN processed_content pc ON rc.id = pc.raw_content_id
WHERE rc.collected_at >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', rc.collected_at)
ORDER BY hour DESC;

-- Daily ingestion summary
CREATE VIEW daily_ingestion_summary AS
SELECT 
    DATE(collected_at) as date,
    source_type,
    COUNT(*) as items_collected,
    COUNT(DISTINCT source_name) as active_sources,
    COUNT(DISTINCT url) as unique_urls
FROM raw_content
WHERE collected_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(collected_at), source_type
ORDER BY date DESC, source_type;

-- ==========================================
-- Triggers for Maintenance
-- ==========================================

-- Update timestamps trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables
CREATE TRIGGER update_raw_content_updated_at BEFORE UPDATE ON raw_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_processed_content_updated_at BEFORE UPDATE ON processed_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_data_sources_updated_at BEFORE UPDATE ON data_sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_batch_jobs_updated_at BEFORE UPDATE ON batch_processing_jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- Initial Data
-- ==========================================

-- Insert initial data sources from current RSS feeds
INSERT INTO data_sources (name, url, source_type, check_interval_minutes, priority, keywords) VALUES
('ICTworks - Funding & AI Opportunities', 'https://www.ictworks.org/feed/', 'rss', 60, 'high', '["AI", "artificial intelligence", "funding", "grants", "Africa"]'),
('Mozilla Foundation - Africa Research Grants', 'https://foundation.mozilla.org/en/blog/rss/', 'rss', 120, 'high', '["AI", "artificial intelligence", "Africa", "research", "grants"]'),
('IDRC - Research & Innovation', 'https://idrc-crdi.ca/rss.xml', 'rss', 60, 'high', '["AI", "AI4D", "artificial intelligence", "machine learning", "digital"]'),
('TechCabal - African Tech', 'https://techcabal.com/feed/', 'rss', 90, 'high', '["AI", "artificial intelligence", "funding", "investment", "startup"]'),
('African Business', 'https://african.business/feed/', 'rss', 120, 'high', '["AI", "artificial intelligence", "technology", "digital", "funding"]'),
('World Bank Blogs', 'https://blogs.worldbank.org/feed', 'rss', 120, 'high', '["AI", "artificial intelligence", "Africa", "digital", "development"]'),
('TechPoint Africa', 'https://techpoint.africa/feed/', 'rss', 90, 'high', '["AI", "artificial intelligence", "funding", "investment", "startup"]'),
('Disrupt Africa', 'https://disrupt-africa.com/feed/', 'rss', 90, 'high', '["AI", "artificial intelligence", "funding", "investment", "startup"]')
ON CONFLICT (url) DO NOTHING;

-- Initialize daily stats for today
INSERT INTO daily_processing_stats (date) VALUES (CURRENT_DATE)
ON CONFLICT (date) DO NOTHING;

-- ==========================================
-- Comments for Documentation
-- ==========================================

COMMENT ON TABLE raw_content IS 'Stores raw content from all data sources - optimized for massive scale ingestion';
COMMENT ON TABLE processed_content IS 'Stores AI-processed content with analysis results';
COMMENT ON TABLE batch_processing_jobs IS 'Tracks batch processing jobs for monitoring and debugging';
COMMENT ON TABLE data_sources IS 'Manages data sources with health monitoring';
COMMENT ON TABLE content_deduplication IS 'Tracks content deduplication for efficiency';
COMMENT ON TABLE daily_processing_stats IS 'Daily statistics for monitoring pipeline performance';

COMMENT ON COLUMN raw_content.content_hash IS 'Generated hash for deduplication based on url+title+content';
COMMENT ON COLUMN raw_content.processing_status IS 'Current processing status: pending, processing, completed, failed';
COMMENT ON COLUMN processed_content.funding_relevance_score IS 'AI-determined relevance score for funding (0-1)';
COMMENT ON COLUMN data_sources.success_rate IS 'Success rate for data collection from this source';
COMMENT ON COLUMN data_sources.consecutive_errors IS 'Number of consecutive errors - used for health monitoring';

COMMENT ON VIEW unprocessed_priority_content IS 'High-priority content waiting for processing';
COMMENT ON VIEW source_health_dashboard IS 'Health status of all data sources';
COMMENT ON VIEW processing_performance IS 'Hourly processing performance metrics';
COMMENT ON VIEW daily_ingestion_summary IS 'Daily summary of data ingestion by source type';

-- Performance hints
COMMENT ON INDEX idx_raw_content_collected_at IS 'Primary index for time-based queries - most common access pattern';
COMMENT ON INDEX idx_raw_content_processing_status IS 'Critical for batch processing job queries';
COMMENT ON INDEX idx_processed_content_relevance IS 'Enables fast retrieval of high-relevance content';