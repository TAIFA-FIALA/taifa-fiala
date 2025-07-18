-- Funding Intelligence Database Schema
-- Based on the Notion note: "Where to go from here? AI-Powered Funding Intelligence Pipeline"

-- ==========================================
-- Core Intelligence Tables
-- ==========================================

-- Funding signals storage - captures all funding-related content with AI analysis
CREATE TABLE funding_signals (
    id SERIAL PRIMARY KEY,
    source_url VARCHAR(1000),
    source_type VARCHAR(50) NOT NULL, -- 'rss', 'news', 'crawl', 'social', 'academic'
    signal_type VARCHAR(50) NOT NULL, -- 'partnership_announcement', 'strategy_launch', 'pilot_success', etc.
    title VARCHAR(500),
    content TEXT NOT NULL,
    original_language VARCHAR(10) DEFAULT 'en',
    processed_content TEXT, -- AI-processed/cleaned content
    
    -- AI Analysis Results
    funding_implications BOOLEAN DEFAULT FALSE,
    confidence_score FLOAT DEFAULT 0.0,
    funding_type VARCHAR(20), -- 'direct', 'indirect', 'potential'
    timeline VARCHAR(20), -- 'immediate', 'short_term', 'long_term'
    priority_score INTEGER DEFAULT 0,
    event_type VARCHAR(50), -- from FundingEventType enum
    expected_funding_date DATE,
    estimated_amount VARCHAR(100),
    
    -- Extracted entities (JSON format)
    extracted_entities JSONB,
    relationships JSONB,
    predictions JSONB,
    suggested_actions JSONB,
    
    -- Analysis metadata
    ai_analysis_version VARCHAR(10) DEFAULT '1.0',
    analysis_rationale TEXT,
    key_insights TEXT,
    
    -- Investigation tracking
    investigation_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'archived'
    investigation_notes TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    
    -- Standard fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    
    -- Indexing
    CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1),
    CONSTRAINT valid_priority CHECK (priority_score >= 0 AND priority_score <= 100)
);

-- Funding entities - organizations, people, programs, etc.
CREATE TABLE funding_entities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300) NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- 'funder', 'recipient', 'intermediary', 'person', 'program', 'location'
    entity_subtype VARCHAR(50), -- 'corporate', 'government', 'foundation', 'startup', 'university', etc.
    
    -- Entity details
    aliases JSONB, -- Alternative names/spellings
    description TEXT,
    website VARCHAR(500),
    location VARCHAR(200),
    sector VARCHAR(100),
    
    -- Funding capacity (for funders)
    estimated_funding_capacity NUMERIC(15,2),
    funding_focus_areas JSONB,
    typical_funding_range VARCHAR(100),
    
    -- Intelligence metadata
    confidence FLOAT DEFAULT 0.0,
    first_seen DATE DEFAULT CURRENT_DATE,
    last_seen DATE DEFAULT CURRENT_DATE,
    mention_count INTEGER DEFAULT 1,
    importance_score INTEGER DEFAULT 0,
    
    -- Attributes (flexible JSON storage)
    attributes JSONB,
    
    -- Verification status
    verification_status VARCHAR(20) DEFAULT 'unverified', -- 'verified', 'unverified', 'disputed'
    verification_notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_entity_confidence CHECK (confidence >= 0 AND confidence <= 1),
    CONSTRAINT valid_importance CHECK (importance_score >= 0 AND importance_score <= 100)
);

-- Funding relationships - who funds whom, partnerships, etc.
CREATE TABLE funding_relationships (
    id SERIAL PRIMARY KEY,
    source_entity_id INTEGER REFERENCES funding_entities(id),
    target_entity_id INTEGER REFERENCES funding_entities(id),
    source_entity_name VARCHAR(300), -- Denormalized for performance
    target_entity_name VARCHAR(300), -- Denormalized for performance
    
    -- Relationship details
    relationship_type VARCHAR(50) NOT NULL, -- 'funds', 'partners_with', 'invests_in', 'sponsors', etc.
    confidence FLOAT DEFAULT 0.0,
    context TEXT,
    amount VARCHAR(100),
    
    -- Timeline
    relationship_date DATE,
    first_seen DATE DEFAULT CURRENT_DATE,
    last_seen DATE DEFAULT CURRENT_DATE,
    total_interactions INTEGER DEFAULT 1,
    
    -- Supporting evidence
    source_content TEXT,
    supporting_urls JSONB,
    evidence_strength VARCHAR(20) DEFAULT 'weak', -- 'strong', 'medium', 'weak'
    
    -- Relationship status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'completed', 'disputed'
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_relationship_confidence CHECK (confidence >= 0 AND confidence <= 1),
    CONSTRAINT no_self_relationship CHECK (source_entity_id != target_entity_id)
);

-- Funding predictions - AI predictions about future opportunities
CREATE TABLE funding_predictions (
    id SERIAL PRIMARY KEY,
    signal_id INTEGER REFERENCES funding_signals(id),
    entity_id INTEGER REFERENCES funding_entities(id),
    
    -- Prediction details
    prediction_type VARCHAR(50) NOT NULL, -- 'funding_opportunity', 'partnership', 'expansion', 'acquisition'
    predicted_opportunity TEXT NOT NULL,
    expected_date DATE,
    confidence FLOAT DEFAULT 0.0,
    rationale TEXT,
    
    -- Prediction metadata
    prediction_model_version VARCHAR(10) DEFAULT '1.0',
    prediction_factors JSONB, -- What factors led to this prediction
    
    -- Tracking
    materialized BOOLEAN DEFAULT FALSE,
    materialized_date DATE,
    materialized_notes TEXT,
    accuracy_score FLOAT, -- How accurate was the prediction (0-1)
    
    -- Follow-up
    monitoring_status VARCHAR(20) DEFAULT 'active', -- 'active', 'monitoring', 'completed', 'failed'
    next_review_date DATE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_prediction_confidence CHECK (confidence >= 0 AND confidence <= 1),
    CONSTRAINT valid_accuracy CHECK (accuracy_score IS NULL OR (accuracy_score >= 0 AND accuracy_score <= 1))
);

-- Funding timelines - track events over time for pattern recognition
CREATE TABLE funding_timelines (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES funding_entities(id),
    signal_id INTEGER REFERENCES funding_signals(id),
    
    -- Event details
    event_date DATE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_description TEXT,
    event_impact_score INTEGER DEFAULT 0, -- 0-100 scale
    
    -- Context
    source_content TEXT,
    context JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_impact_score CHECK (event_impact_score >= 0 AND event_impact_score <= 100)
);

-- Pattern recognition - identified patterns in funding behavior
CREATE TABLE funding_patterns (
    id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(100) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL, -- 'temporal', 'behavioral', 'sector-specific'
    
    -- Pattern details
    description TEXT,
    pattern_data JSONB, -- Flexible storage for pattern specifics
    confidence FLOAT DEFAULT 0.0,
    
    -- Pattern metrics
    occurrence_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    average_delay_days INTEGER,
    
    -- Entities involved
    primary_entity_id INTEGER REFERENCES funding_entities(id),
    secondary_entity_id INTEGER REFERENCES funding_entities(id),
    
    -- Pattern lifecycle
    first_observed DATE,
    last_observed DATE,
    pattern_status VARCHAR(20) DEFAULT 'active', -- 'active', 'deprecated', 'emerging'
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_pattern_confidence CHECK (confidence >= 0 AND confidence <= 1),
    CONSTRAINT valid_success_rate CHECK (success_rate >= 0 AND success_rate <= 1)
);

-- Success story analysis - learn from successful funding cases
CREATE TABLE success_stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    
    -- Success details
    recipient_entity_id INTEGER REFERENCES funding_entities(id),
    funder_entity_id INTEGER REFERENCES funding_entities(id),
    funding_amount VARCHAR(100),
    funding_date DATE,
    
    -- Success factors
    success_factors JSONB,
    key_lessons JSONB,
    replicable_elements JSONB,
    
    -- Analysis
    analyzed_by_ai BOOLEAN DEFAULT FALSE,
    ai_insights TEXT,
    similar_opportunities JSONB,
    
    -- Source tracking
    source_url VARCHAR(1000),
    source_content TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conference and event intelligence
CREATE TABLE event_intelligence (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(300) NOT NULL,
    event_type VARCHAR(50), -- 'conference', 'summit', 'workshop', 'webinar'
    event_date DATE,
    location VARCHAR(200),
    
    -- Event details
    description TEXT,
    sponsors JSONB,
    speakers JSONB,
    themes JSONB,
    side_events JSONB,
    
    -- Funding implications
    funding_announcements JSONB,
    potential_opportunities JSONB,
    decision_makers_present JSONB,
    
    -- Intelligence scores
    funding_potential_score INTEGER DEFAULT 0,
    network_value_score INTEGER DEFAULT 0,
    
    -- Tracking
    monitored BOOLEAN DEFAULT FALSE,
    follow_up_required BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_funding_potential CHECK (funding_potential_score >= 0 AND funding_potential_score <= 100),
    CONSTRAINT valid_network_value CHECK (network_value_score >= 0 AND network_value_score <= 100)
);

-- ==========================================
-- Indexes for Performance
-- ==========================================

-- Funding signals indexes
CREATE INDEX idx_funding_signals_type ON funding_signals(signal_type);
CREATE INDEX idx_funding_signals_confidence ON funding_signals(confidence_score DESC);
CREATE INDEX idx_funding_signals_priority ON funding_signals(priority_score DESC);
CREATE INDEX idx_funding_signals_date ON funding_signals(created_at DESC);
CREATE INDEX idx_funding_signals_funding_implications ON funding_signals(funding_implications);
CREATE INDEX idx_funding_signals_investigation_status ON funding_signals(investigation_status);

-- Funding entities indexes
CREATE INDEX idx_funding_entities_type ON funding_entities(entity_type);
CREATE INDEX idx_funding_entities_name ON funding_entities(name);
CREATE INDEX idx_funding_entities_importance ON funding_entities(importance_score DESC);
CREATE INDEX idx_funding_entities_last_seen ON funding_entities(last_seen DESC);
CREATE INDEX idx_funding_entities_location ON funding_entities(location);

-- Funding relationships indexes
CREATE INDEX idx_funding_relationships_source ON funding_relationships(source_entity_id);
CREATE INDEX idx_funding_relationships_target ON funding_relationships(target_entity_id);
CREATE INDEX idx_funding_relationships_type ON funding_relationships(relationship_type);
CREATE INDEX idx_funding_relationships_confidence ON funding_relationships(confidence DESC);
CREATE INDEX idx_funding_relationships_date ON funding_relationships(relationship_date DESC);

-- Funding predictions indexes
CREATE INDEX idx_funding_predictions_entity ON funding_predictions(entity_id);
CREATE INDEX idx_funding_predictions_confidence ON funding_predictions(confidence DESC);
CREATE INDEX idx_funding_predictions_expected_date ON funding_predictions(expected_date);
CREATE INDEX idx_funding_predictions_materialized ON funding_predictions(materialized);

-- Funding timelines indexes
CREATE INDEX idx_funding_timelines_entity ON funding_timelines(entity_id);
CREATE INDEX idx_funding_timelines_event_date ON funding_timelines(event_date DESC);
CREATE INDEX idx_funding_timelines_event_type ON funding_timelines(event_type);

-- Event intelligence indexes
CREATE INDEX idx_event_intelligence_date ON event_intelligence(event_date DESC);
CREATE INDEX idx_event_intelligence_funding_potential ON event_intelligence(funding_potential_score DESC);
CREATE INDEX idx_event_intelligence_monitored ON event_intelligence(monitored);

-- ==========================================
-- JSON Indexes for JSONB columns
-- ==========================================

-- Funding signals JSON indexes
CREATE INDEX idx_funding_signals_entities_gin ON funding_signals USING gin(extracted_entities);
CREATE INDEX idx_funding_signals_relationships_gin ON funding_signals USING gin(relationships);
CREATE INDEX idx_funding_signals_predictions_gin ON funding_signals USING gin(predictions);

-- Funding entities JSON indexes
CREATE INDEX idx_funding_entities_aliases_gin ON funding_entities USING gin(aliases);
CREATE INDEX idx_funding_entities_attributes_gin ON funding_entities USING gin(attributes);
CREATE INDEX idx_funding_entities_funding_focus_gin ON funding_entities USING gin(funding_focus_areas);

-- ==========================================
-- Views for Common Queries
-- ==========================================

-- High-priority funding signals
CREATE VIEW high_priority_signals AS
SELECT 
    id,
    signal_type,
    title,
    confidence_score,
    priority_score,
    funding_type,
    timeline,
    expected_funding_date,
    estimated_amount,
    created_at
FROM funding_signals
WHERE funding_implications = TRUE
  AND priority_score >= 70
  AND investigation_status = 'pending'
ORDER BY priority_score DESC, confidence_score DESC;

-- Active funding relationships
CREATE VIEW active_funding_relationships AS
SELECT 
    fr.id,
    fr.source_entity_name,
    fr.target_entity_name,
    fr.relationship_type,
    fr.confidence,
    fr.amount,
    fr.relationship_date,
    se.entity_type as source_type,
    te.entity_type as target_type
FROM funding_relationships fr
JOIN funding_entities se ON fr.source_entity_id = se.id
JOIN funding_entities te ON fr.target_entity_id = te.id
WHERE fr.status = 'active'
  AND fr.confidence >= 0.5
ORDER BY fr.confidence DESC, fr.relationship_date DESC;

-- Upcoming predicted opportunities
CREATE VIEW upcoming_opportunities AS
SELECT 
    fp.id,
    fp.predicted_opportunity,
    fp.expected_date,
    fp.confidence,
    fp.rationale,
    fe.name as entity_name,
    fe.entity_type,
    fs.title as source_signal
FROM funding_predictions fp
JOIN funding_entities fe ON fp.entity_id = fe.id
LEFT JOIN funding_signals fs ON fp.signal_id = fs.id
WHERE fp.materialized = FALSE
  AND fp.monitoring_status = 'active'
  AND fp.expected_date >= CURRENT_DATE
ORDER BY fp.expected_date ASC, fp.confidence DESC;

-- Recent funding activity
CREATE VIEW recent_funding_activity AS
SELECT 
    'signal' as activity_type,
    fs.id,
    fs.title as activity_title,
    fs.signal_type as activity_subtype,
    fs.confidence_score as score,
    fs.created_at as activity_date
FROM funding_signals fs
WHERE fs.funding_implications = TRUE
  AND fs.created_at >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT 
    'relationship' as activity_type,
    fr.id,
    fr.source_entity_name || ' ' || fr.relationship_type || ' ' || fr.target_entity_name as activity_title,
    fr.relationship_type as activity_subtype,
    fr.confidence as score,
    fr.created_at as activity_date
FROM funding_relationships fr
WHERE fr.created_at >= CURRENT_DATE - INTERVAL '30 days'

ORDER BY activity_date DESC;

-- ==========================================
-- Triggers for Maintenance
-- ==========================================

-- Update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_funding_signals_updated_at BEFORE UPDATE ON funding_signals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_funding_entities_updated_at BEFORE UPDATE ON funding_entities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_funding_relationships_updated_at BEFORE UPDATE ON funding_relationships FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_funding_predictions_updated_at BEFORE UPDATE ON funding_predictions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_funding_patterns_updated_at BEFORE UPDATE ON funding_patterns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_success_stories_updated_at BEFORE UPDATE ON success_stories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_event_intelligence_updated_at BEFORE UPDATE ON event_intelligence FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- Seed Data
-- ==========================================

-- Insert some known funding entities
INSERT INTO funding_entities (name, entity_type, entity_subtype, description, website, location, sector, estimated_funding_capacity, funding_focus_areas, confidence, importance_score) VALUES
('World Bank', 'funder', 'multilateral', 'International financial institution providing loans and grants to governments', 'https://worldbank.org', 'Global', 'Development', 50000000000, '["digital development", "AI", "education", "health"]', 1.0, 100),
('African Development Bank', 'funder', 'multilateral', 'Regional development bank for Africa', 'https://afdb.org', 'Africa', 'Development', 10000000000, '["infrastructure", "digital transformation", "innovation"]', 1.0, 95),
('Google', 'funder', 'corporate', 'Technology company with AI focus', 'https://google.com', 'Global', 'Technology', 5000000000, '["AI", "digital skills", "startup acceleration"]', 1.0, 90),
('Microsoft', 'funder', 'corporate', 'Technology company with AI initiatives', 'https://microsoft.com', 'Global', 'Technology', 3000000000, '["AI for Good", "digital transformation", "skills development"]', 1.0, 90),
('Bill & Melinda Gates Foundation', 'funder', 'foundation', 'Philanthropic foundation focused on global development', 'https://gatesfoundation.org', 'Global', 'Development', 2000000000, '["health", "education", "digital financial services"]', 1.0, 85),
('Y Combinator', 'intermediary', 'accelerator', 'Startup accelerator program', 'https://ycombinator.com', 'Global', 'Technology', 100000000, '["startup acceleration", "AI", "fintech"]', 1.0, 80),
('Techstars', 'intermediary', 'accelerator', 'Global startup accelerator network', 'https://techstars.com', 'Global', 'Technology', 50000000, '["startup acceleration", "mentorship", "network"]', 1.0, 75);

-- Insert some funding patterns
INSERT INTO funding_patterns (pattern_name, pattern_type, description, confidence, occurrence_count, success_rate, average_delay_days) VALUES
('Corporate Partnership to Funding', 'temporal', 'Corporate partnerships typically lead to funding announcements within 90 days', 0.8, 25, 0.75, 90),
('Government Strategy to Grant Program', 'temporal', 'Government AI strategies typically result in grant programs within 180 days', 0.85, 15, 0.8, 180),
('Pilot Success to Scale-up Funding', 'temporal', 'Successful pilot programs typically receive scale-up funding within 120 days', 0.7, 20, 0.65, 120),
('Conference Announcement to Opportunity', 'temporal', 'Major conference announcements often lead to funding opportunities within 60 days', 0.6, 30, 0.55, 60);

-- Comments for documentation
COMMENT ON TABLE funding_signals IS 'Stores all funding-related content with AI analysis results';
COMMENT ON TABLE funding_entities IS 'Organizations, people, programs, and locations in the funding ecosystem';
COMMENT ON TABLE funding_relationships IS 'Relationships between entities (who funds whom, partnerships, etc.)';
COMMENT ON TABLE funding_predictions IS 'AI predictions about future funding opportunities';
COMMENT ON TABLE funding_timelines IS 'Timeline of events for pattern recognition';
COMMENT ON TABLE funding_patterns IS 'Identified patterns in funding behavior';
COMMENT ON TABLE success_stories IS 'Analysis of successful funding cases';
COMMENT ON TABLE event_intelligence IS 'Intelligence gathered from conferences and events';

COMMENT ON COLUMN funding_signals.signal_type IS 'Type of funding signal: partnership_announcement, strategy_launch, pilot_success, investment_round, etc.';
COMMENT ON COLUMN funding_signals.funding_implications IS 'Whether this content has funding implications (AI determined)';
COMMENT ON COLUMN funding_signals.confidence_score IS 'AI confidence in funding relevance (0-1)';
COMMENT ON COLUMN funding_signals.priority_score IS 'Priority score for investigation (0-100)';
COMMENT ON COLUMN funding_signals.extracted_entities IS 'JSON of entities extracted by AI (funders, recipients, amounts, etc.)';
COMMENT ON COLUMN funding_signals.relationships IS 'JSON of relationships identified in the content';
COMMENT ON COLUMN funding_signals.predictions IS 'JSON of AI predictions based on this signal';

COMMENT ON COLUMN funding_entities.entity_type IS 'Primary entity type: funder, recipient, intermediary, person, program, location';
COMMENT ON COLUMN funding_entities.entity_subtype IS 'More specific type: corporate, government, foundation, startup, university, etc.';
COMMENT ON COLUMN funding_entities.estimated_funding_capacity IS 'Estimated total funding capacity in USD';
COMMENT ON COLUMN funding_entities.funding_focus_areas IS 'JSON array of focus areas for funding';
COMMENT ON COLUMN funding_entities.importance_score IS 'Importance in the funding ecosystem (0-100)';

COMMENT ON COLUMN funding_relationships.relationship_type IS 'Type of relationship: funds, partners_with, invests_in, sponsors, etc.';
COMMENT ON COLUMN funding_relationships.evidence_strength IS 'Strength of evidence for this relationship: strong, medium, weak';
COMMENT ON COLUMN funding_relationships.total_interactions IS 'Number of times this relationship has been observed';

COMMENT ON COLUMN funding_predictions.prediction_type IS 'Type of prediction: funding_opportunity, partnership, expansion, acquisition';
COMMENT ON COLUMN funding_predictions.materialized IS 'Whether the prediction came true';
COMMENT ON COLUMN funding_predictions.accuracy_score IS 'How accurate the prediction was (0-1)';

COMMENT ON VIEW high_priority_signals IS 'High-priority funding signals requiring immediate investigation';
COMMENT ON VIEW active_funding_relationships IS 'Currently active and high-confidence funding relationships';
COMMENT ON VIEW upcoming_opportunities IS 'Predicted funding opportunities in the near future';
COMMENT ON VIEW recent_funding_activity IS 'Recent funding-related activity across all tables';