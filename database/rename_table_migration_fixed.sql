-- Fixed Table Rename Migration: africa_intelligence_feed -> africa_intelligence_feed
-- This migration renames the table to better reflect its actual content

-- Step 1: Create the new table with the same structure
CREATE TABLE africa_intelligence_feed AS 
SELECT * FROM africa_intelligence_feed;

-- Step 2: Add new columns for better content classification
ALTER TABLE africa_intelligence_feed 
ADD COLUMN IF NOT EXISTS content_category VARCHAR(50) DEFAULT 'general',
ADD COLUMN IF NOT EXISTS relevance_score DECIMAL(3,2) DEFAULT 0.5,
ADD COLUMN IF NOT EXISTS ai_extracted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS geographic_focus VARCHAR(100),
ADD COLUMN IF NOT EXISTS sector_tags TEXT[];

-- Step 3: Update funding_type values to be more descriptive
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

-- Step 4: Update content categories based on analysis
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

-- Step 5: Extract geographic focus from title and description
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
    WHEN title ILIKE '%malawi%' OR description ILIKE '%malawi%' THEN 'Malawi'
    WHEN title ILIKE '%zambia%' OR description ILIKE '%zambia%' THEN 'Zambia'
    WHEN title ILIKE '%zimbabwe%' OR description ILIKE '%zimbabwe%' THEN 'Zimbabwe'
    WHEN title ILIKE '%botswana%' OR description ILIKE '%botswana%' THEN 'Botswana'
    WHEN title ILIKE '%namibia%' OR description ILIKE '%namibia%' THEN 'Namibia'
    WHEN title ILIKE '%eswatini%' OR description ILIKE '%eswatini%' THEN 'Eswatini'
    WHEN title ILIKE '%liberia%' OR description ILIKE '%liberia%' THEN 'Liberia'
    WHEN title ILIKE '%africa%' OR description ILIKE '%africa%' THEN 'Pan-African'
    ELSE 'Unknown'
END;

-- Step 6: Create indexes on the new table
CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_source_type ON africa_intelligence_feed(source_type);
CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_created_at ON africa_intelligence_feed(created_at);
CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_funding_type ON africa_intelligence_feed(funding_type);
CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_status ON africa_intelligence_feed(status);
CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_content_category ON africa_intelligence_feed(content_category);
CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_geographic_focus ON africa_intelligence_feed(geographic_focus);

-- Step 7: Add table and column comments
COMMENT ON TABLE africa_intelligence_feed IS 'AI-powered intelligence feed collecting news, intelligence feed, policy updates, and technology developments across Africa';
COMMENT ON COLUMN africa_intelligence_feed.title IS 'Title of intelligence item (news, funding, policy, etc.)';
COMMENT ON COLUMN africa_intelligence_feed.description IS 'Description or summary of the intelligence item';
COMMENT ON COLUMN africa_intelligence_feed.funding_type IS 'Type of item: funding, news, policy, tech, etc.';
COMMENT ON COLUMN africa_intelligence_feed.content_category IS 'Main category: funding, technology, policy, health, education, climate, economy, general';
COMMENT ON COLUMN africa_intelligence_feed.geographic_focus IS 'Primary geographic focus (country or region)';
COMMENT ON COLUMN africa_intelligence_feed.relevance_score IS 'AI-calculated relevance score (0.0 to 1.0)';

-- Step 8: Show migration results
SELECT 
    'Migration completed successfully!' as status,
    COUNT(*) as total_records,
    COUNT(CASE WHEN content_category = 'funding' THEN 1 END) as funding_items,
    COUNT(CASE WHEN content_category = 'technology' THEN 1 END) as tech_items,
    COUNT(CASE WHEN content_category = 'policy' THEN 1 END) as policy_items,
    COUNT(CASE WHEN content_category = 'general' THEN 1 END) as general_items,
    COUNT(CASE WHEN geographic_focus != 'Unknown' THEN 1 END) as items_with_geographic_focus
FROM africa_intelligence_feed;

-- Step 9: Show sample of categorized data
SELECT 
    title,
    content_category,
    geographic_focus,
    funding_type,
    created_at
FROM africa_intelligence_feed 
ORDER BY created_at DESC 
LIMIT 10;

-- Note: After testing the new table, you can:
-- 1. Drop the old table: DROP TABLE africa_intelligence_feed;
-- 2. Or rename it for backup: ALTER TABLE africa_intelligence_feed RENAME TO africa_intelligence_feed_backup;