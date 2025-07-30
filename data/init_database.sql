-- TAIFA-FIALA SQLite Database Schema
-- Initialize the funding opportunities database for n8n integration

-- Create funding_opportunities table
CREATE TABLE IF NOT EXISTS funding_opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Basic Information
    title TEXT NOT NULL,
    description TEXT,
    organization TEXT NOT NULL,
    
    -- Financial Details
    amount_exact REAL,
    amount_min REAL,
    amount_max REAL,
    currency TEXT DEFAULT 'USD',
    
    -- Dates
    deadline DATE,
    announcement_date DATE,
    funding_start_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Location & Targeting
    location TEXT,
    country TEXT,
    region TEXT,
    sector TEXT,
    stage TEXT,
    
    -- Requirements & Process
    eligibility TEXT,
    application_url TEXT,
    application_process TEXT,
    selection_criteria TEXT,
    
    -- Metadata
    source_url TEXT,
    source_type TEXT, -- 'rss', 'api', 'manual', 'scrape'
    validation_status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    relevance_score REAL DEFAULT 0.5,
    
    -- Additional Fields
    tags TEXT, -- JSON array as text
    project_duration TEXT,
    reporting_requirements TEXT,
    target_audience TEXT,
    ai_subsectors TEXT,
    development_stage TEXT,
    
    -- Flags
    is_active BOOLEAN DEFAULT 1,
    is_open BOOLEAN DEFAULT 1,
    requires_registration BOOLEAN DEFAULT 0,
    collaboration_required BOOLEAN DEFAULT 0,
    gender_focused BOOLEAN DEFAULT 0,
    youth_focused BOOLEAN DEFAULT 0,
    
    -- Search & Analytics
    view_count INTEGER DEFAULT 0,
    last_checked DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_funding_deadline ON funding_opportunities(deadline);
CREATE INDEX IF NOT EXISTS idx_funding_sector ON funding_opportunities(sector);
CREATE INDEX IF NOT EXISTS idx_funding_location ON funding_opportunities(location);
CREATE INDEX IF NOT EXISTS idx_funding_organization ON funding_opportunities(organization);
CREATE INDEX IF NOT EXISTS idx_funding_active ON funding_opportunities(is_active, is_open);
CREATE INDEX IF NOT EXISTS idx_funding_validation ON funding_opportunities(validation_status);
CREATE INDEX IF NOT EXISTS idx_funding_created ON funding_opportunities(created_at);

-- Create organizations table for normalization
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    website TEXT,
    description TEXT,
    type TEXT, -- 'foundation', 'government', 'corporate', 'ngo'
    location TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create funding_sources table for tracking data sources
CREATE TABLE IF NOT EXISTS funding_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    url TEXT,
    source_type TEXT, -- 'rss', 'api', 'website'
    last_checked DATETIME,
    is_active BOOLEAN DEFAULT 1,
    check_frequency INTEGER DEFAULT 3600, -- seconds
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create pipeline_logs table for n8n monitoring
CREATE TABLE IF NOT EXISTS pipeline_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    execution_id TEXT, -- n8n execution ID
    status TEXT, -- 'success', 'error', 'warning'
    records_processed INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    error_message TEXT,
    execution_time REAL, -- seconds
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (source_id) REFERENCES funding_sources(id)
);

-- Insert default funding sources
INSERT OR IGNORE INTO funding_sources (name, url, source_type) VALUES
('African Development Bank', 'https://www.afdb.org/en/news-and-events/news', 'website'),
('Gates Foundation', 'https://www.gatesfoundation.org/ideas/media-center/press-releases', 'website'),
('World Bank', 'https://www.worldbank.org/en/news/all', 'website'),
('Google AI for Social Good', 'https://ai.google/social-good/', 'website'),
('Mozilla Foundation', 'https://foundation.mozilla.org/en/blog/', 'rss');

-- Insert sample organizations
INSERT OR IGNORE INTO organizations (name, type, location) VALUES
('African Development Bank', 'development', 'Abidjan, Côte d''Ivoire'),
('Gates Foundation', 'foundation', 'Seattle, USA'),
('World Bank', 'development', 'Washington DC, USA'),
('Google.org', 'corporate', 'Mountain View, USA'),
('Mozilla Foundation', 'foundation', 'San Francisco, USA');

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_funding_opportunities_timestamp 
    AFTER UPDATE ON funding_opportunities
BEGIN
    UPDATE funding_opportunities 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Create view for active opportunities
CREATE VIEW IF NOT EXISTS active_opportunities AS
SELECT 
    *,
    CASE 
        WHEN deadline IS NULL THEN 'No deadline'
        WHEN DATE(deadline) < DATE('now') THEN 'Expired'
        WHEN DATE(deadline) <= DATE('now', '+30 days') THEN 'Closing soon'
        ELSE 'Open'
    END as deadline_status
FROM funding_opportunities 
WHERE is_active = 1 AND validation_status = 'approved';

-- Create view for pipeline monitoring
CREATE VIEW IF NOT EXISTS pipeline_stats AS
SELECT 
    fs.name as source_name,
    COUNT(pl.id) as total_executions,
    SUM(CASE WHEN pl.status = 'success' THEN 1 ELSE 0 END) as successful_executions,
    SUM(CASE WHEN pl.status = 'error' THEN 1 ELSE 0 END) as failed_executions,
    SUM(pl.records_inserted) as total_records_inserted,
    AVG(pl.execution_time) as avg_execution_time,
    MAX(pl.created_at) as last_execution
FROM funding_sources fs
LEFT JOIN pipeline_logs pl ON fs.id = pl.source_id
GROUP BY fs.id, fs.name;