-- Source Validation Module Database Schema
-- This migration adds all tables required for the source validation workflow

-- Source submissions table - stores all submitted sources
CREATE TABLE IF NOT EXISTS source_submissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    contact_person VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    update_frequency VARCHAR(50) NOT NULL,
    geographic_focus TEXT[], -- Array of geographic regions
    expected_volume VARCHAR(20) NOT NULL,
    sample_urls TEXT[], -- Array of sample URLs
    ai_relevance_estimate INTEGER CHECK (ai_relevance_estimate BETWEEN 0 AND 100),
    africa_relevance_estimate INTEGER CHECK (africa_relevance_estimate BETWEEN 0 AND 100),
    language VARCHAR(20) NOT NULL,
    submitter_role VARCHAR(100) NOT NULL,
    has_permission BOOLEAN NOT NULL DEFAULT false,
    preferred_contact VARCHAR(50) NOT NULL,
    
    -- Validation results
    validation_score FLOAT CHECK (validation_score BETWEEN 0 AND 1),
    validation_recommendation VARCHAR(20), -- accept, reject, needs_review
    validation_checks JSONB,
    validation_issues TEXT[],
    validation_suggestions TEXT[],
    validated_at TIMESTAMP,
    
    -- Source classification
    source_classification JSONB,
    
    -- Pilot information
    pilot_id INTEGER,
    
    -- Manual review
    requires_manual_review BOOLEAN DEFAULT false,
    manual_review_queued_at TIMESTAMP,
    
    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'submitted',
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_for_pilot_at TIMESTAMP,
    production_active_at TIMESTAMP,
    rejected_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient queries
CREATE INDEX idx_source_submissions_status ON source_submissions(status);
CREATE INDEX idx_source_submissions_submitted_at ON source_submissions(submitted_at);
CREATE INDEX idx_source_submissions_validation_score ON source_submissions(validation_score);

-- Manual review queue table
CREATE TABLE IF NOT EXISTS manual_review_queue (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES source_submissions(id),
    validation_score FLOAT,
    issues TEXT[],
    suggestions TEXT[],
    priority VARCHAR(10) NOT NULL DEFAULT 'medium', -- high, medium, low
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, in_review, completed
    
    -- Review process
    assigned_reviewer VARCHAR(255),
    assigned_at TIMESTAMP,
    decision VARCHAR(20), -- approve, reject
    reviewer_notes TEXT,
    reviewed_at TIMESTAMP,
    
    -- Metadata
    queued_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for review queue
CREATE INDEX idx_manual_review_queue_status ON manual_review_queue(status);
CREATE INDEX idx_manual_review_queue_priority ON manual_review_queue(priority);

-- Pilot monitoring table
CREATE TABLE IF NOT EXISTS pilot_monitoring (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES source_submissions(id),
    source_id INTEGER, -- References data_sources table
    source_name VARCHAR(255) NOT NULL,
    source_url TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    
    -- Configuration
    monitoring_config JSONB,
    classification_data JSONB,
    
    -- Pilot period
    pilot_start_date TIMESTAMP NOT NULL,
    pilot_end_date TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, extended, completed, failed
    
    -- Performance evaluation
    performance_metrics JSONB,
    pilot_outcome VARCHAR(30), -- approve_for_production, extend_pilot, reject
    evaluation_completed_at TIMESTAMP,
    
    -- Extension handling
    extension_reason TEXT,
    extensions_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for pilot monitoring
CREATE INDEX idx_pilot_monitoring_status ON pilot_monitoring(status);
CREATE INDEX idx_pilot_monitoring_source_id ON pilot_monitoring(source_id);
CREATE INDEX idx_pilot_monitoring_end_date ON pilot_monitoring(pilot_end_date);

-- Source performance metrics table
CREATE TABLE IF NOT EXISTS source_performance_metrics (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL, -- References data_sources table
    evaluation_period_days INTEGER NOT NULL,
    
    -- Volume metrics
    opportunities_discovered INTEGER NOT NULL DEFAULT 0,
    ai_relevant_count INTEGER NOT NULL DEFAULT 0,
    africa_relevant_count INTEGER NOT NULL DEFAULT 0,
    funding_relevant_count INTEGER NOT NULL DEFAULT 0,
    
    -- Quality metrics
    community_approval_rate FLOAT CHECK (community_approval_rate BETWEEN 0 AND 1),
    duplicate_rate FLOAT CHECK (duplicate_rate BETWEEN 0 AND 1),
    data_completeness_score FLOAT CHECK (data_completeness_score BETWEEN 0 AND 1),
    
    -- Technical metrics
    monitoring_reliability FLOAT CHECK (monitoring_reliability BETWEEN 0 AND 1),
    processing_error_rate FLOAT CHECK (processing_error_rate BETWEEN 0 AND 1),
    average_response_time FLOAT, -- in milliseconds
    
    -- Value metrics
    unique_opportunities_added INTEGER NOT NULL DEFAULT 0,
    high_value_opportunities INTEGER NOT NULL DEFAULT 0,
    successful_applications INTEGER NOT NULL DEFAULT 0,
    
    -- Overall assessment
    overall_score FLOAT CHECK (overall_score BETWEEN 0 AND 1),
    performance_status VARCHAR(20) NOT NULL, -- excellent, good, acceptable, poor, failing
    
    -- Timestamps
    calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    next_evaluation TIMESTAMP
);

-- Index for performance metrics
CREATE INDEX idx_source_performance_metrics_source_id ON source_performance_metrics(source_id);
CREATE INDEX idx_source_performance_metrics_calculated_at ON source_performance_metrics(calculated_at);
CREATE INDEX idx_source_performance_metrics_overall_score ON source_performance_metrics(overall_score);

-- Deduplication logs table
CREATE TABLE IF NOT EXISTS deduplication_logs (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER, -- May reference africa_intelligence_feed table
    source_table VARCHAR(50), -- Which table the content came from
    source_content_id INTEGER, -- ID in the source table
    
    -- Deduplication results
    results JSONB NOT NULL, -- Full deduplication pipeline results
    is_duplicate BOOLEAN NOT NULL,
    action_taken VARCHAR(30) NOT NULL, -- proceed_to_validation, reject_before_validation
    
    -- Match details
    primary_match_type VARCHAR(30), -- exact_url, exact_content, semantic_similarity, etc.
    similarity_score FLOAT,
    existing_opportunity_id INTEGER,
    
    -- Metadata
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER
);

-- Index for deduplication logs
CREATE INDEX idx_deduplication_logs_opportunity_id ON deduplication_logs(opportunity_id);
CREATE INDEX idx_deduplication_logs_is_duplicate ON deduplication_logs(is_duplicate);
CREATE INDEX idx_deduplication_logs_checked_at ON deduplication_logs(checked_at);

-- Source monitoring logs table (for technical monitoring)
CREATE TABLE IF NOT EXISTS source_monitoring_logs (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL, -- References data_sources table
    pilot_id INTEGER, -- References pilot_monitoring table if applicable
    
    -- Monitoring attempt details
    monitoring_strategy VARCHAR(50) NOT NULL,
    check_type VARCHAR(30) NOT NULL, -- scheduled, manual, webhook
    
    -- Results
    success BOOLEAN NOT NULL,
    response_time_ms INTEGER,
    opportunities_found INTEGER DEFAULT 0,
    new_opportunities INTEGER DEFAULT 0,
    
    -- Error handling
    error_message TEXT,
    error_type VARCHAR(50),
    retry_attempt INTEGER DEFAULT 0,
    
    -- HTTP details (if applicable)
    http_status_code INTEGER,
    content_length INTEGER,
    content_type VARCHAR(100),
    
    -- Metadata
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    scheduled_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Index for monitoring logs
CREATE INDEX idx_source_monitoring_logs_source_id ON source_monitoring_logs(source_id);
CREATE INDEX idx_source_monitoring_logs_checked_at ON source_monitoring_logs(checked_at);
CREATE INDEX idx_source_monitoring_logs_success ON source_monitoring_logs(success);

-- Application outcomes table (for tracking funding application success)
CREATE TABLE IF NOT EXISTS application_outcomes (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER NOT NULL, -- References africa_intelligence_feed table
    user_id INTEGER, -- References users table if available
    applicant_organization VARCHAR(255),
    applicant_email VARCHAR(255),
    
    -- Application details
    applied_at TIMESTAMP,
    application_deadline TIMESTAMP,
    amount_requested DECIMAL(15,2),
    amount_awarded DECIMAL(15,2),
    
    -- Outcome
    outcome VARCHAR(20) NOT NULL, -- successful, unsuccessful, pending, withdrawn
    outcome_date TIMESTAMP,
    outcome_notes TEXT,
    
    -- Follow-up
    feedback_provided BOOLEAN DEFAULT false,
    feedback_text TEXT,
    willing_to_share_story BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for application outcomes
CREATE INDEX idx_application_outcomes_opportunity_id ON application_outcomes(opportunity_id);
CREATE INDEX idx_application_outcomes_outcome ON application_outcomes(outcome);
CREATE INDEX idx_application_outcomes_applied_at ON application_outcomes(applied_at);

-- Add content hash column to africa_intelligence_feed table for deduplication
-- (This may already exist, so using IF NOT EXISTS equivalent)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'content_hash'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN content_hash VARCHAR(64);
        CREATE INDEX idx_africa_intelligence_feed_content_hash ON africa_intelligence_feed(content_hash);
    END IF;
END $$;

-- Add embedding column for semantic similarity (if using vector embeddings)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'embedding'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN embedding FLOAT[];
    END IF;
END $$;

-- Add source validation related columns to africa_intelligence_feed
DO $$ 
BEGIN
    -- Agent scores from CrewAI processing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'agent_scores'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN agent_scores JSONB;
    END IF;
    
    -- Processing metadata
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'processing_metadata'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN processing_metadata JSONB;
    END IF;
    
    -- Conflicts detected during processing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'conflicts_detected'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN conflicts_detected JSONB;
    END IF;
    
    -- Resolution applied to conflicts
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'resolution_applied'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN resolution_applied JSONB;
    END IF;
    
    -- Review status for community validation
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'review_status'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN review_status VARCHAR(50) DEFAULT 'pending';
        CREATE INDEX idx_africa_intelligence_feed_review_status ON africa_intelligence_feed(review_status);
    END IF;
    
    -- Confidence score from processing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'confidence_score'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1);
    END IF;
END $$;

-- Add source validation related columns to data_sources table
DO $$ 
BEGIN
    -- Pilot mode flag
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'data_sources' 
        AND column_name = 'pilot_mode'
    ) THEN
        ALTER TABLE data_sources ADD COLUMN pilot_mode BOOLEAN DEFAULT false;
    END IF;
    
    -- Pilot ID reference
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'data_sources' 
        AND column_name = 'pilot_id'
    ) THEN
        ALTER TABLE data_sources ADD COLUMN pilot_id INTEGER;
    END IF;
    
    -- Production promotion timestamp
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'data_sources' 
        AND column_name = 'promoted_to_production_at'
    ) THEN
        ALTER TABLE data_sources ADD COLUMN promoted_to_production_at TIMESTAMP;
    END IF;
    
    -- Deprecation tracking
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'data_sources' 
        AND column_name = 'deprecated_at'
    ) THEN
        ALTER TABLE data_sources ADD COLUMN deprecated_at TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'data_sources' 
        AND column_name = 'deprecation_reason'
    ) THEN
        ALTER TABLE data_sources ADD COLUMN deprecation_reason TEXT;
    END IF;
END $$;

-- Create foreign key constraints
ALTER TABLE source_submissions 
    ADD CONSTRAINT fk_source_submissions_pilot_id 
    FOREIGN KEY (pilot_id) REFERENCES pilot_monitoring(id);

ALTER TABLE pilot_monitoring 
    ADD CONSTRAINT fk_pilot_monitoring_submission_id 
    FOREIGN KEY (submission_id) REFERENCES source_submissions(id);

-- Create update timestamp triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_source_submissions_updated_at 
    BEFORE UPDATE ON source_submissions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pilot_monitoring_updated_at 
    BEFORE UPDATE ON pilot_monitoring 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_application_outcomes_updated_at 
    BEFORE UPDATE ON application_outcomes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial performance thresholds configuration
INSERT INTO configuration (key, value, description) VALUES
    ('source_validation.min_ai_relevance', '0.30', 'Minimum AI relevance threshold for source approval'),
    ('source_validation.min_africa_relevance', '0.50', 'Minimum Africa relevance threshold for source approval'),
    ('source_validation.min_community_approval', '0.70', 'Minimum community approval rate for source approval'),
    ('source_validation.max_duplicate_rate', '0.20', 'Maximum allowed duplicate rate for source approval'),
    ('source_validation.min_monitoring_reliability', '0.95', 'Minimum monitoring reliability for source approval'),
    ('source_validation.pilot_duration_days', '30', 'Default pilot monitoring period in days'),
    ('source_validation.performance_evaluation_frequency_days', '30', 'How often to evaluate source performance')
ON CONFLICT (key) DO NOTHING;

-- Create materialized view for source validation dashboard
CREATE MATERIALIZED VIEW IF NOT EXISTS source_validation_dashboard AS
SELECT 
    COUNT(*) as total_submissions,
    COUNT(*) FILTER (WHERE status = 'submitted') as pending_validation,
    COUNT(*) FILTER (WHERE status = 'validating') as in_manual_review,
    COUNT(*) FILTER (WHERE status = 'approved_for_pilot') as approved_for_pilot,
    COUNT(*) FILTER (WHERE status = 'pilot_active') as pilot_active,
    COUNT(*) FILTER (WHERE status = 'production_active') as production_active,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
    AVG(validation_score) as avg_validation_score,
    COUNT(*) FILTER (WHERE submitted_at >= NOW() - INTERVAL '7 days') as submissions_this_week,
    COUNT(*) FILTER (WHERE submitted_at >= NOW() - INTERVAL '30 days') as submissions_this_month
FROM source_submissions;

-- Create index on materialized view
CREATE UNIQUE INDEX idx_source_validation_dashboard ON source_validation_dashboard((1));

-- Refresh the materialized view
REFRESH MATERIALIZED VIEW source_validation_dashboard;

-- Comments for documentation
COMMENT ON TABLE source_submissions IS 'Stores all community-submitted funding sources for validation';
COMMENT ON TABLE manual_review_queue IS 'Queue for sources requiring manual review by TAIFA team';
COMMENT ON TABLE pilot_monitoring IS 'Tracks 30-day pilot monitoring periods for approved sources';
COMMENT ON TABLE source_performance_metrics IS 'Performance metrics calculated for each source over time';
COMMENT ON TABLE deduplication_logs IS 'Logs all deduplication checks to prevent duplicate opportunities';
COMMENT ON TABLE source_monitoring_logs IS 'Technical monitoring logs for source availability and reliability';
COMMENT ON TABLE application_outcomes IS 'Tracks success rates of funding applications from discovered opportunities';

-- Grant permissions (adjust based on your user roles)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO taifa_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO taifa_app;
