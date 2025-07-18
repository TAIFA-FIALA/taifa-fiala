-- Table Rename Migration: africa_intelligence_feed -> africa_intelligence_feed
-- This migration renames the table to better reflect its actual content:
-- AI-powered intelligence feed about Africa (news, funding, policy, tech, etc.)

-- Step 1: Create the new table with the same structure
CREATE TABLE IF NOT EXISTS africa_intelligence_feed AS 
SELECT * FROM africa_intelligence_feed;

-- Step 2: Update the table comment to reflect new purpose
COMMENT ON TABLE africa_intelligence_feed IS 'AI-powered intelligence feed collecting news, intelligence feed, policy updates, and technology developments across Africa';

-- Step 3: Update column comments to reflect broader content types
COMMENT ON COLUMN africa_intelligence_feed.title IS 'Title of intelligence item (news, funding, policy, etc.)';
COMMENT ON COLUMN africa_intelligence_feed.description IS 'Description or summary of the intelligence item';
COMMENT ON COLUMN africa_intelligence_feed.funding_type IS 'Type of item: funding, news, policy, tech, etc.';
COMMENT ON COLUMN africa_intelligence_feed.funding_amount IS 'Amount (if applicable for funding items)';
COMMENT ON COLUMN africa_intelligence_feed.source_type IS 'Source type: rss, serper_search, web_scraping, etc.';
COMMENT ON COLUMN africa_intelligence_feed.source_url IS 'Original source URL';
COMMENT ON COLUMN africa_intelligence_feed.additional_notes IS 'Additional context and metadata';

-- Step 4: Create indexes on the new table
CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_source_type ON africa_intelligence_feed(source_type);
CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_created_at ON africa_intelligence_feed(created_at);
CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_funding_type ON africa_intelligence_feed(funding_type);
CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_status ON africa_intelligence_feed(status);

-- Step 5: Update funding_type values to be more descriptive
UPDATE africa_intelligence_feed 
SET funding_type = CASE 
    WHEN title ILIKE '%funding%' OR title ILIKE '%grant%' OR title ILIKE '%investment%' THEN 'funding'
    WHEN title ILIKE '%startup%' OR title ILIKE '%accelerator%' OR title ILIKE '%incubator%' THEN 'startup_news'
    WHEN title ILIKE '%AI%' OR title ILIKE '%artificial intelligence%' OR title ILIKE '%technology%' OR title ILIKE '%tech%' THEN 'tech_news'
    WHEN title ILIKE '%policy%' OR title ILIKE '%government%' OR title ILIKE '%regulation%' THEN 'policy_news'
    WHEN title ILIKE '%health%' OR title ILIKE '%medical%' OR title ILIKE '%healthcare%' THEN 'health_news'
    WHEN title ILIKE '%education%' OR title ILIKE '%university%' OR title ILIKE '%school%' THEN 'education_news'
    WHEN title ILIKE '%climate%' OR title ILIKE '%environment%' OR title ILIKE '%sustainability%' THEN 'climate_news'
    WHEN title ILIKE '%economy%' OR title ILIKE '%economic%' OR title ILIKE '%business%' THEN 'economic_news'
    ELSE 'general_news'
END
WHERE funding_type = 'opportunity' OR funding_type IS NULL;

-- Step 6: Add new columns for better content classification
ALTER TABLE africa_intelligence_feed 
ADD COLUMN IF NOT EXISTS content_category VARCHAR(50) DEFAULT 'general',
ADD COLUMN IF NOT EXISTS relevance_score DECIMAL(3,2) DEFAULT 0.5,
ADD COLUMN IF NOT EXISTS ai_extracted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS geographic_focus VARCHAR(100),
ADD COLUMN IF NOT EXISTS sector_tags TEXT[];

-- Step 7: Update content categories based on analysis
UPDATE africa_intelligence_feed 
SET content_category = CASE 
    WHEN funding_type = 'funding' THEN 'funding'
    WHEN funding_type IN ('tech_news', 'startup_news') THEN 'technology'
    WHEN funding_type = 'policy_news' THEN 'policy'
    WHEN funding_type = 'health_news' THEN 'health'
    WHEN funding_type = 'education_news' THEN 'education'
    WHEN funding_type = 'climate_news' THEN 'climate'
    WHEN funding_type = 'economic_news' THEN 'economy'
    ELSE 'general'
END;

-- Step 8: Extract geographic focus from title and description
UPDATE africa_intelligence_feed 
SET geographic_focus = CASE 
    WHEN title ILIKE '%south africa%' OR description ILIKE '%south africa%' THEN 'South Africa'
    WHEN title ILIKE '%nigeria%' OR description ILIKE '%nigeria%' THEN 'Nigeria'
    WHEN title ILIKE '%kenya%' OR description ILIKE '%kenya%' THEN 'Kenya'
    WHEN title ILIKE '%ghana%' OR description ILIKE '%ghana%' THEN 'Ghana'
    WHEN title ILIKE '%uganda%' OR description ILIKE '%uganda%' THEN 'Uganda'
    WHEN title ILIKE '%tanzania%' OR description ILIKE '%tanzania%' THEN 'Tanzania'
    WHEN title ILIKE '%rwanda%' OR description ILIKE '%rwanda%' THEN 'Rwanda'
    WHEN title ILIKE '%egypt%' OR description ILIKE '%egypt%' THEN 'Egypt'
    WHEN title ILIKE '%morocco%' OR description ILIKE '%morocco%' THEN 'Morocco'
    WHEN title ILIKE '%ethiopia%' OR description ILIKE '%ethiopia%' THEN 'Ethiopia'
    WHEN title ILIKE '%africa%' OR description ILIKE '%africa%' THEN 'Pan-African'
    ELSE NULL
END;

-- Step 9: Create a view with the old name for backward compatibility
CREATE OR REPLACE VIEW africa_intelligence_feed AS 
SELECT * FROM africa_intelligence_feed 
WHERE content_category = 'funding' OR funding_type = 'funding';

-- Step 10: Success message
SELECT 
    'Table renamed to africa_intelligence_feed!' as status,
    COUNT(*) as total_records,
    COUNT(CASE WHEN content_category = 'funding' THEN 1 END) as funding_items,
    COUNT(CASE WHEN content_category = 'technology' THEN 1 END) as tech_items,
    COUNT(CASE WHEN content_category = 'policy' THEN 1 END) as policy_items,
    COUNT(CASE WHEN content_category = 'general' THEN 1 END) as general_items
FROM africa_intelligence_feed;

-- Note: After testing, you can drop the old table with:
-- DROP TABLE africa_intelligence_feed CASCADE;