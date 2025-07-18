-- Create RSS Feeds Management Table
-- This table stores RSS feed configurations for the TAIFA-FIALA system

CREATE TABLE IF NOT EXISTS rss_feeds (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(2000) NOT NULL UNIQUE,
    description TEXT,
    
    -- Feed categorization
    category VARCHAR(100) DEFAULT 'general',
    region VARCHAR(100) DEFAULT 'africa',
    language VARCHAR(10) DEFAULT 'en',
    
    -- Collection settings
    keywords JSONB DEFAULT '[]'::jsonb,
    check_interval_minutes INTEGER DEFAULT 60,
    max_items_per_check INTEGER DEFAULT 50,
    
    -- Feed status
    is_active BOOLEAN DEFAULT true,
    last_checked TIMESTAMP WITH TIME ZONE,
    last_successful_check TIMESTAMP WITH TIME ZONE,
    total_items_collected INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    
    -- Feed validation
    feed_title VARCHAR(500),
    feed_description TEXT,
    feed_language VARCHAR(10),
    item_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES auth.users(id),
    
    -- Performance metrics
    avg_response_time_ms INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    
    -- Content filtering
    exclude_keywords JSONB DEFAULT '[]'::jsonb,
    min_content_length INTEGER DEFAULT 100,
    
    -- Source credibility
    credibility_score INTEGER DEFAULT 50 CHECK (credibility_score >= 0 AND credibility_score <= 100),
    
    CONSTRAINT valid_check_interval CHECK (check_interval_minutes >= 5),
    CONSTRAINT valid_max_items CHECK (max_items_per_check >= 1 AND max_items_per_check <= 1000)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_rss_feeds_active ON rss_feeds(is_active);
CREATE INDEX IF NOT EXISTS idx_rss_feeds_category ON rss_feeds(category);
CREATE INDEX IF NOT EXISTS idx_rss_feeds_region ON rss_feeds(region);
CREATE INDEX IF NOT EXISTS idx_rss_feeds_next_check ON rss_feeds(last_checked, check_interval_minutes);
CREATE INDEX IF NOT EXISTS idx_rss_feeds_url ON rss_feeds(url);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_rss_feeds_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER rss_feeds_updated_at
    BEFORE UPDATE ON rss_feeds
    FOR EACH ROW
    EXECUTE FUNCTION update_rss_feeds_updated_at();

-- Enable RLS
ALTER TABLE rss_feeds ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Public read access" ON rss_feeds FOR SELECT USING (true);
CREATE POLICY "Authenticated users can insert" ON rss_feeds FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update feeds they created" ON rss_feeds FOR UPDATE USING (auth.uid() = created_by OR auth.role() = 'service_role');
CREATE POLICY "Service role full access" ON rss_feeds FOR ALL USING (auth.role() = 'service_role');

-- Insert some default RSS feeds
INSERT INTO rss_feeds (name, url, description, category, region, keywords, check_interval_minutes, credibility_score) VALUES
('AllAfrica Technology News', 'https://allafrica.com/tools/headlines/rdf/technology/headlines.rdf', 'Technology news across Africa', 'technology', 'africa', '["AI", "artificial intelligence", "technology", "innovation", "startup"]', 60, 85),
('TechCentral South Africa', 'https://techcentral.co.za/feed/', 'South African technology news', 'technology', 'south_africa', '["AI", "technology", "startup", "funding", "innovation"]', 45, 90),
('VentureBurn', 'https://ventureburn.com/feed/', 'African startup and venture capital news', 'business', 'africa', '["startup", "funding", "investment", "venture capital", "AI"]', 30, 88),
('African Business Technology', 'https://african.business/technology/feed', 'African business technology coverage', 'business', 'africa', '["technology", "business", "AI", "digital transformation"]', 90, 80),
('IT News Africa', 'https://www.itnewsafrica.com/feed/', 'IT and technology news across Africa', 'technology', 'africa', '["AI", "technology", "ICT", "digital", "innovation"]', 120, 75)
ON CONFLICT (url) DO NOTHING;

-- Create a view for active feeds
CREATE OR REPLACE VIEW active_rss_feeds AS
SELECT 
    id,
    name,
    url,
    description,
    category,
    region,
    keywords,
    check_interval_minutes,
    last_checked,
    total_items_collected,
    success_rate,
    credibility_score,
    created_at
FROM rss_feeds
WHERE is_active = true
ORDER BY credibility_score DESC, total_items_collected DESC;

-- Success message
SELECT 'RSS feeds table created successfully!' as message;
SELECT 'Default RSS feeds added!' as message;
SELECT COUNT(*) as "Total RSS Feeds" FROM rss_feeds;