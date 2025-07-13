-- TAIFA CrewAI Enhanced Database Schema
-- Support for learning, conflict resolution, and rejection analysis
-- Implementation Date: July 11, 2025

-- =======================================================
-- AGENT PROCESSING LOGS FOR LEARNING
-- =======================================================

-- Agent processing logs for learning and performance monitoring
CREATE TABLE IF NOT EXISTS agent_processing_logs (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER REFERENCES funding_opportunities(id),
    agent_name VARCHAR(100) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    processing_time_ms INTEGER DEFAULT 0,
    confidence_score FLOAT DEFAULT 0.0,
    errors_encountered JSONB DEFAULT '[]',
    warnings_encountered JSONB DEFAULT '[]',
    memory_usage_mb INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Index for performance queries
    INDEX idx_agent_logs_opportunity (opportunity_id),
    INDEX idx_agent_logs_agent (agent_name),
    INDEX idx_agent_logs_confidence (confidence_score),
    INDEX idx_agent_logs_created (created_at)
);

-- =======================================================
-- REJECTION DATABASE FOR LEARNING
-- =======================================================

-- Comprehensive rejection tracking for continuous learning
CREATE TABLE IF NOT EXISTS rejected_opportunities (
    id SERIAL PRIMARY KEY,
    original_url VARCHAR(500),
    raw_content TEXT,
    agent_outputs JSONB,
    rejection_reason VARCHAR(200) NOT NULL,
    rejection_category VARCHAR(50), -- 'low_confidence', 'ai_irrelevant', 'not_africa', 'not_funding', 'error'
    overall_confidence_score FLOAT DEFAULT 0.0,
    individual_scores JSONB, -- Store all agent confidence scores
    
    -- Human review tracking
    human_review_notes TEXT,
    human_reviewer_id VARCHAR(100),
    human_decision VARCHAR(50), -- 'confirmed_rejection', 'should_approve', 'needs_reprocessing'
    human_reviewed_at TIMESTAMP,
    
    -- Reprocessing tracking
    should_reprocess BOOLEAN DEFAULT FALSE,
    reprocessed_at TIMESTAMP,
    reprocessing_notes TEXT,
    
    -- Learning flags
    learning_value VARCHAR(50), -- 'high', 'medium', 'low' - how valuable for improving agents
    pattern_category VARCHAR(100), -- Categorize rejection patterns
    
    -- Metadata
    source_type VARCHAR(50) DEFAULT 'serper_search',
    processing_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for analysis
    INDEX idx_rejected_category (rejection_category),
    INDEX idx_rejected_confidence (overall_confidence_score),
    INDEX idx_rejected_human_review (human_decision),
    INDEX idx_rejected_reprocess (should_reprocess),
    INDEX idx_rejected_learning (learning_value),
    INDEX idx_rejected_created (created_at)
);

-- =======================================================
-- CONFLICT RESOLUTION TRACKING
-- =======================================================

-- Track conflicts between agents and their resolutions
CREATE TABLE IF NOT EXISTS conflict_resolutions (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER REFERENCES funding_opportunities(id),
    batch_id VARCHAR(100), -- Group conflicts from same processing batch
    
    -- Conflict details
    conflict_type VARCHAR(100) NOT NULL, -- 'amount_parsing', 'organization_identification', etc.
    conflicting_values JSONB NOT NULL,
    agents_involved VARCHAR(200)[], -- Array of agent names
    confidence_difference FLOAT DEFAULT 0.0,
    
    -- Resolution details
    resolution_method VARCHAR(100), -- 'higher_confidence', 'database_lookup', 'manual_review'
    final_value JSONB,
    resolution_confidence FLOAT DEFAULT 0.0,
    
    -- Validation tracking
    human_validated BOOLEAN DEFAULT FALSE,
    human_validation_result VARCHAR(50), -- 'correct', 'incorrect', 'partial'
    human_validator_id VARCHAR(100),
    validation_notes TEXT,
    validated_at TIMESTAMP,
    
    -- Learning metadata
    resolution_accuracy FLOAT, -- Set after human validation
    learned_pattern BOOLEAN DEFAULT FALSE, -- Whether this helped improve agents
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for analysis
    INDEX idx_conflicts_type (conflict_type),
    INDEX idx_conflicts_opportunity (opportunity_id),
    INDEX idx_conflicts_resolution (resolution_method),
    INDEX idx_conflicts_validated (human_validated),
    INDEX idx_conflicts_accuracy (resolution_accuracy),
    INDEX idx_conflicts_created (created_at)
);

-- =======================================================
-- ORGANIZATION KNOWLEDGE BASE
-- =======================================================

-- Enhanced organizations table with learning metadata
ALTER TABLE organizations 
ADD COLUMN IF NOT EXISTS ai_relevant BOOLEAN DEFAULT NULL,
ADD COLUMN IF NOT EXISTS funding_focus TEXT[], -- Array of funding focus areas
ADD COLUMN IF NOT EXISTS confidence_score FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS validation_status VARCHAR(50) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS last_encountered_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS encounter_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS learning_priority VARCHAR(20) DEFAULT 'medium';

-- Organization learning metadata
CREATE TABLE IF NOT EXISTS organization_learning_metadata (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    
    -- Learning statistics
    times_correctly_identified INTEGER DEFAULT 0,
    times_missed INTEGER DEFAULT 0,
    times_confused_with JSONB DEFAULT '[]', -- Track common confusion patterns
    
    -- Agent performance with this organization
    avg_identification_confidence FLOAT DEFAULT 0.0,
    best_identifying_agent VARCHAR(100),
    common_name_variations TEXT[],
    
    -- Pattern metadata
    typical_funding_amounts JSONB, -- Store range and patterns
    typical_funding_types TEXT[],
    typical_geographic_scope TEXT[],
    seasonal_patterns JSONB, -- When they typically announce funding
    
    -- Quality tracking
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_count INTEGER DEFAULT 0,
    data_quality_score FLOAT DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_org_learning_org (organization_id),
    INDEX idx_org_learning_confidence (avg_identification_confidence),
    INDEX idx_org_learning_updated (last_updated)
);

-- =======================================================
-- PROCESSING BATCH TRACKING
-- =======================================================

-- Track processing batches for analysis and rollback
CREATE TABLE IF NOT EXISTS processing_batches (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'serper_search', 'rss_feed', 'manual_submission'
    
    -- Batch statistics
    total_items INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    approved_items INTEGER DEFAULT 0,
    community_review_items INTEGER DEFAULT 0,
    human_review_items INTEGER DEFAULT 0,
    rejected_items INTEGER DEFAULT 0,
    error_items INTEGER DEFAULT 0,
    
    -- Performance metrics
    avg_processing_time_ms INTEGER DEFAULT 0,
    avg_confidence_score FLOAT DEFAULT 0.0,
    total_conflicts INTEGER DEFAULT 0,
    
    -- Metadata
    processing_version VARCHAR(50),
    agent_configuration JSONB, -- Store agent settings for this batch
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'processing', -- 'processing', 'completed', 'failed', 'cancelled'
    
    -- Error tracking
    error_summary TEXT,
    error_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_batches_batch_id (batch_id),
    INDEX idx_batches_source (source_type),
    INDEX idx_batches_status (status),
    INDEX idx_batches_started (started_at)
);

-- =======================================================
-- ENHANCED FUNDING OPPORTUNITIES
-- =======================================================

-- Add CrewAI-specific fields to existing funding_opportunities table
ALTER TABLE funding_opportunities 
ADD COLUMN IF NOT EXISTS processing_metadata JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS agent_scores JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS conflicts_detected JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS resolution_applied JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS review_status VARCHAR(50) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS overall_confidence_score FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS processing_batch_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS needs_community_review BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS community_review_deadline TIMESTAMP,
ADD COLUMN IF NOT EXISTS auto_publish_at TIMESTAMP;

-- =======================================================
-- COMMUNITY VALIDATION SYSTEM
-- =======================================================

-- Community validation tracking
CREATE TABLE IF NOT EXISTS community_validations (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER REFERENCES funding_opportunities(id),
    validator_user_id VARCHAR(100) NOT NULL,
    
    -- Validation details
    validation_type VARCHAR(50) NOT NULL, -- 'approve', 'reject', 'flag_issue', 'suggest_edit'
    validation_reason TEXT,
    suggested_changes JSONB,
    confidence_in_validation VARCHAR(20), -- 'high', 'medium', 'low'
    
    -- Validation categories
    relevance_feedback VARCHAR(50), -- 'highly_relevant', 'somewhat_relevant', 'not_relevant'
    accuracy_feedback VARCHAR(50), -- 'accurate', 'mostly_accurate', 'inaccurate'
    completeness_feedback VARCHAR(50), -- 'complete', 'missing_info', 'needs_details'
    
    -- Response tracking
    moderator_response TEXT,
    moderator_action VARCHAR(50), -- 'accepted', 'rejected', 'needs_discussion'
    responded_at TIMESTAMP,
    
    -- Metadata
    validation_source VARCHAR(50) DEFAULT 'newsletter', -- 'newsletter', 'dashboard', 'api'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate validations
    UNIQUE(opportunity_id, validator_user_id, validation_type),
    
    -- Indexes
    INDEX idx_community_val_opportunity (opportunity_id),
    INDEX idx_community_val_validator (validator_user_id),
    INDEX idx_community_val_type (validation_type),
    INDEX idx_community_val_created (created_at)
);

-- =======================================================
-- LEARNING PERFORMANCE METRICS
-- =======================================================

-- Track agent performance over time for learning insights
CREATE TABLE IF NOT EXISTS agent_performance_metrics (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    metric_date DATE DEFAULT CURRENT_DATE,
    
    -- Processing statistics
    total_processed INTEGER DEFAULT 0,
    avg_confidence_score FLOAT DEFAULT 0.0,
    avg_processing_time_ms INTEGER DEFAULT 0,
    
    -- Accuracy metrics (based on human validation)
    validated_correct INTEGER DEFAULT 0,
    validated_incorrect INTEGER DEFAULT 0,
    accuracy_rate FLOAT DEFAULT 0.0,
    
    -- Conflict statistics
    conflicts_caused INTEGER DEFAULT 0,
    conflicts_resolved_correctly INTEGER DEFAULT 0,
    
    -- Learning progression
    improvement_rate FLOAT DEFAULT 0.0, -- Week-over-week improvement
    learning_events_count INTEGER DEFAULT 0, -- Number of times agent was updated
    
    -- Resource usage
    avg_memory_usage_mb INTEGER DEFAULT 0,
    total_api_calls INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10,4) DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure one record per agent per day
    UNIQUE(agent_name, metric_date),
    
    -- Indexes
    INDEX idx_performance_agent (agent_name),
    INDEX idx_performance_date (metric_date),
    INDEX idx_performance_accuracy (accuracy_rate)
);

-- =======================================================
-- LEARNING PATTERN RECOGNITION
-- =======================================================

-- Store identified patterns for agent improvement
CREATE TABLE IF NOT EXISTS learning_patterns (
    id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(100) NOT NULL, -- 'organization_naming', 'amount_formatting', 'date_parsing'
    pattern_name VARCHAR(200) NOT NULL,
    pattern_description TEXT,
    
    -- Pattern details
    pattern_regex VARCHAR(500),
    pattern_examples JSONB,
    pattern_confidence FLOAT DEFAULT 0.0,
    
    -- Usage statistics
    times_applied INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    last_successful_use TIMESTAMP,
    
    -- Learning metadata
    discovered_by VARCHAR(50), -- 'agent_analysis', 'human_input', 'automated_discovery'
    discovery_batch_id VARCHAR(100),
    validation_status VARCHAR(50) DEFAULT 'pending',
    
    -- Lifecycle
    is_active BOOLEAN DEFAULT TRUE,
    deprecated_reason TEXT,
    replaced_by_pattern_id INTEGER REFERENCES learning_patterns(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_patterns_type (pattern_type),
    INDEX idx_patterns_active (is_active),
    INDEX idx_patterns_success (success_rate),
    INDEX idx_patterns_created (created_at)
);

-- =======================================================
-- HELPER FUNCTIONS FOR LEARNING
-- =======================================================

-- Function to update organization encounter statistics
CREATE OR REPLACE FUNCTION update_organization_encounter(
    p_org_name VARCHAR(200),
    p_confidence_score FLOAT DEFAULT 0.0,
    p_correctly_identified BOOLEAN DEFAULT TRUE
) RETURNS INTEGER AS $$
DECLARE
    org_id INTEGER;
BEGIN
    -- Find or create organization
    INSERT INTO organizations (name, encounter_count, last_encountered_at, confidence_score)
    VALUES (p_org_name, 1, CURRENT_TIMESTAMP, p_confidence_score)
    ON CONFLICT (name) DO UPDATE SET
        encounter_count = organizations.encounter_count + 1,
        last_encountered_at = CURRENT_TIMESTAMP,
        confidence_score = (organizations.confidence_score + p_confidence_score) / 2
    RETURNING id INTO org_id;
    
    -- Update learning metadata
    INSERT INTO organization_learning_metadata (organization_id, times_correctly_identified, times_missed)
    VALUES (org_id, 
            CASE WHEN p_correctly_identified THEN 1 ELSE 0 END,
            CASE WHEN p_correctly_identified THEN 0 ELSE 1 END)
    ON CONFLICT (organization_id) DO UPDATE SET
        times_correctly_identified = organization_learning_metadata.times_correctly_identified + 
            CASE WHEN p_correctly_identified THEN 1 ELSE 0 END,
        times_missed = organization_learning_metadata.times_missed + 
            CASE WHEN p_correctly_identified THEN 0 ELSE 1 END,
        avg_identification_confidence = (organization_learning_metadata.avg_identification_confidence + p_confidence_score) / 2,
        last_updated = CURRENT_TIMESTAMP;
    
    RETURN org_id;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate agent performance trends
CREATE OR REPLACE FUNCTION calculate_agent_performance_trend(
    p_agent_name VARCHAR(100),
    p_days_back INTEGER DEFAULT 7
) RETURNS JSONB AS $$
DECLARE
    current_performance RECORD;
    previous_performance RECORD;
    trend_data JSONB;
BEGIN
    -- Get current period performance
    SELECT AVG(accuracy_rate) as accuracy, AVG(avg_confidence_score) as confidence,
           AVG(avg_processing_time_ms) as processing_time
    INTO current_performance
    FROM agent_performance_metrics
    WHERE agent_name = p_agent_name 
    AND metric_date >= CURRENT_DATE - p_days_back;
    
    -- Get previous period performance
    SELECT AVG(accuracy_rate) as accuracy, AVG(avg_confidence_score) as confidence,
           AVG(avg_processing_time_ms) as processing_time
    INTO previous_performance
    FROM agent_performance_metrics
    WHERE agent_name = p_agent_name 
    AND metric_date >= CURRENT_DATE - (p_days_back * 2)
    AND metric_date < CURRENT_DATE - p_days_back;
    
    -- Calculate trends
    trend_data = jsonb_build_object(
        'accuracy_trend', 
        CASE WHEN previous_performance.accuracy > 0 
             THEN (current_performance.accuracy - previous_performance.accuracy) / previous_performance.accuracy
             ELSE 0 END,
        'confidence_trend',
        CASE WHEN previous_performance.confidence > 0
             THEN (current_performance.confidence - previous_performance.confidence) / previous_performance.confidence
             ELSE 0 END,
        'speed_trend',
        CASE WHEN previous_performance.processing_time > 0
             THEN (previous_performance.processing_time - current_performance.processing_time) / previous_performance.processing_time
             ELSE 0 END,
        'current_accuracy', current_performance.accuracy,
        'current_confidence', current_performance.confidence,
        'current_processing_time', current_performance.processing_time
    );
    
    RETURN trend_data;
END;
$$ LANGUAGE plpgsql;

-- =======================================================
-- VIEWS FOR MONITORING AND ANALYSIS
-- =======================================================

-- Daily processing summary view
CREATE OR REPLACE VIEW daily_processing_summary AS
SELECT 
    DATE(created_at) as processing_date,
    COUNT(*) as total_processed,
    COUNT(*) FILTER (WHERE review_status = 'auto_approved') as auto_approved,
    COUNT(*) FILTER (WHERE review_status = 'community_review_queue') as community_review,
    COUNT(*) FILTER (WHERE review_status = 'human_review_queue') as human_review,
    COUNT(*) FILTER (WHERE review_status = 'rejection_database') as rejected,
    AVG(overall_confidence_score) as avg_confidence,
    AVG(JSONB_ARRAY_LENGTH(conflicts_detected)) as avg_conflicts_per_item,
    COUNT(DISTINCT processing_batch_id) as processing_batches
FROM funding_opportunities
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY processing_date DESC;

-- Agent performance comparison view
CREATE OR REPLACE VIEW agent_performance_comparison AS
SELECT 
    agent_name,
    AVG(accuracy_rate) as avg_accuracy,
    AVG(avg_confidence_score) as avg_confidence,
    AVG(avg_processing_time_ms) as avg_processing_time,
    SUM(total_processed) as total_items_processed,
    SUM(conflicts_caused) as total_conflicts,
    calculate_agent_performance_trend(agent_name, 7) as weekly_trend
FROM agent_performance_metrics
WHERE metric_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY agent_name
ORDER BY avg_accuracy DESC, avg_confidence DESC;

-- Rejection analysis view
CREATE OR REPLACE VIEW rejection_analysis AS
SELECT 
    rejection_category,
    COUNT(*) as rejection_count,
    AVG(overall_confidence_score) as avg_confidence_at_rejection,
    COUNT(*) FILTER (WHERE human_decision = 'should_approve') as human_overrides,
    COUNT(*) FILTER (WHERE human_decision = 'confirmed_rejection') as human_confirmations,
    COUNT(*) FILTER (WHERE should_reprocess = TRUE) as marked_for_reprocessing,
    COUNT(*) FILTER (WHERE learning_value = 'high') as high_learning_value
FROM rejected_opportunities
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY rejection_category
ORDER BY rejection_count DESC;

-- =======================================================
-- INDEXES FOR PERFORMANCE
-- =======================================================

-- Additional indexes for the new tables
CREATE INDEX IF NOT EXISTS idx_funding_confidence ON funding_opportunities(overall_confidence_score);
CREATE INDEX IF NOT EXISTS idx_funding_review_status ON funding_opportunities(review_status);
CREATE INDEX IF NOT EXISTS idx_funding_batch ON funding_opportunities(processing_batch_id);
CREATE INDEX IF NOT EXISTS idx_funding_community_deadline ON funding_opportunities(community_review_deadline);

-- =======================================================
-- FINAL SUCCESS MESSAGE
-- =======================================================

DO $$ 
BEGIN 
    RAISE NOTICE '🤖 TAIFA CrewAI Enhanced Database Schema Complete!';
    RAISE NOTICE '📊 Learning Tables: agent_processing_logs, rejected_opportunities, conflict_resolutions';
    RAISE NOTICE '🧠 Knowledge Base: organization_learning_metadata, learning_patterns';
    RAISE NOTICE '📈 Performance Tracking: agent_performance_metrics, processing_batches';
    RAISE NOTICE '👥 Community System: community_validations';
    RAISE NOTICE '🔍 Analysis Views: daily_processing_summary, agent_performance_comparison, rejection_analysis';
    RAISE NOTICE '⚡ Ready for: Intelligent learning and continuous improvement!';
END $$;