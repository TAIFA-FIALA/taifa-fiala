-- Scraping Queue System Schema
-- This creates a queue-based system for web scraping where the main engine
-- queues URLs for scraping when it needs more detailed information

-- Scraping queue table
CREATE TABLE IF NOT EXISTS scraping_queue (
    id SERIAL PRIMARY KEY,
    url VARCHAR(1000) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium', -- 'high', 'medium', 'low'
    scraping_instructions JSONB,
    requested_fields TEXT[], -- Array of fields needed
    source_opportunity_id INTEGER, -- Links back to africa_intelligence_feed if applicable
    source_context TEXT, -- Additional context about why this needs scraping
    
    -- Queue management
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed', 'retrying'
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    
    -- Scheduling
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Results
    scraped_data JSONB,
    error_message TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Scraping results table (for storing successful scrapes)
CREATE TABLE IF NOT EXISTS scraping_results (
    id SERIAL PRIMARY KEY,
    queue_id INTEGER REFERENCES scraping_queue(id) ON DELETE CASCADE,
    url VARCHAR(1000) NOT NULL,
    
    -- Extracted data
    title TEXT,
    description TEXT,
    content TEXT,
    amount VARCHAR(100),
    deadline DATE,
    eligibility_criteria TEXT,
    application_process TEXT,
    contact_information TEXT,
    
    -- Additional fields
    extracted_fields JSONB,
    raw_html TEXT,
    
    -- Quality metrics
    extraction_confidence DECIMAL(3,2), -- 0.00 to 1.00
    data_completeness DECIMAL(3,2), -- 0.00 to 1.00
    
    -- Metadata
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Scraping templates table (for reusable scraping instructions)
CREATE TABLE IF NOT EXISTS scraping_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    domain VARCHAR(255), -- e.g., "idrc.ca", "gatesfoundation.org"
    
    -- Scraping configuration
    selectors JSONB, -- CSS selectors for different fields
    extraction_rules JSONB, -- Rules for extracting and cleaning data
    required_fields TEXT[], -- Fields that must be extracted
    
    -- Metadata
    success_rate DECIMAL(3,2) DEFAULT 0.00,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Queue processor status table
CREATE TABLE IF NOT EXISTS scraping_queue_status (
    id SERIAL PRIMARY KEY,
    processor_id VARCHAR(100) UNIQUE, -- UUID for each processor instance
    status VARCHAR(20) DEFAULT 'idle', -- 'idle', 'processing', 'error', 'stopped'
    current_queue_id INTEGER REFERENCES scraping_queue(id),
    
    -- Performance metrics
    items_processed INTEGER DEFAULT 0,
    items_succeeded INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_scraping_queue_status_priority ON scraping_queue(status, priority, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_scraping_queue_url ON scraping_queue(url);
CREATE INDEX IF NOT EXISTS idx_scraping_queue_source_opportunity ON scraping_queue(source_opportunity_id);
CREATE INDEX IF NOT EXISTS idx_scraping_results_queue_id ON scraping_results(queue_id);
CREATE INDEX IF NOT EXISTS idx_scraping_templates_domain ON scraping_templates(domain);

-- Insert some initial scraping templates
INSERT INTO scraping_templates (name, description, domain, selectors, extraction_rules, required_fields) VALUES
('IDRC Funding Template', 'Template for IDRC intelligence feed', 'idrc-crdi.ca', 
 '{"title": ".views-field-title a, .views-field-title", "description": ".views-field-body, .views-field-field-summary", "deadline": ".views-field-field-deadline, .deadline", "amount": ".amount, .funding-amount, .grant-amount"}',
 '{"title": {"clean": true, "max_length": 500}, "description": {"clean": true, "max_length": 5000}, "deadline": {"parse_date": true}, "amount": {"extract_numbers": true}}',
 ARRAY['title', 'description']),

('Gates Foundation Template', 'Template for Gates Foundation challenges', 'gatesfoundation.org', 
 '{"title": "h1, h2, .challenge-title", "description": ".challenge-description, .summary", "deadline": ".deadline, .closing-date", "amount": ".award-amount, .funding-amount"}',
 '{"title": {"clean": true, "max_length": 500}, "description": {"clean": true, "max_length": 5000}, "deadline": {"parse_date": true}, "amount": {"extract_numbers": true}}',
 ARRAY['title', 'description']),

('Generic Funding Template', 'Generic template for unknown funding sources', null, 
 '{"title": "h1, h2, h3, .title", "description": ".description, .summary, p", "deadline": ".deadline, .closing-date, .application-deadline", "amount": ".amount, .funding-amount, .grant-amount, .award-amount"}',
 '{"title": {"clean": true, "max_length": 500}, "description": {"clean": true, "max_length": 5000}, "deadline": {"parse_date": true}, "amount": {"extract_numbers": true}}',
 ARRAY['title', 'description']);

-- Success message
SELECT 'Scraping Queue System schema created successfully!' as message;