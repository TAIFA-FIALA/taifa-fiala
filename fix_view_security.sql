-- Fix Security Definer View Issue
-- This script removes the problematic view and creates a safe replacement

-- 1. Drop the existing view completely
DROP VIEW IF EXISTS active_rss_feeds CASCADE;

-- 2. Create a new view WITHOUT any security definer properties
CREATE VIEW active_rss_feeds 
WITH (security_invoker = true) AS
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

-- 3. Alternative: If the above still causes issues, create a simple function instead
CREATE OR REPLACE FUNCTION get_active_rss_feeds()
RETURNS TABLE(
    id INTEGER,
    name VARCHAR(255),
    url VARCHAR(2000),
    description TEXT,
    category VARCHAR(100),
    region VARCHAR(100),
    keywords JSONB,
    check_interval_minutes INTEGER,
    last_checked TIMESTAMP WITH TIME ZONE,
    total_items_collected INTEGER,
    success_rate FLOAT,
    credibility_score INTEGER,
    created_at TIMESTAMP WITH TIME ZONE
) 
LANGUAGE SQL
SECURITY INVOKER
AS $$
    SELECT 
        rss_feeds.id,
        rss_feeds.name,
        rss_feeds.url,
        rss_feeds.description,
        rss_feeds.category,
        rss_feeds.region,
        rss_feeds.keywords,
        rss_feeds.check_interval_minutes,
        rss_feeds.last_checked,
        rss_feeds.total_items_collected,
        rss_feeds.success_rate,
        rss_feeds.credibility_score,
        rss_feeds.created_at
    FROM rss_feeds
    WHERE rss_feeds.is_active = true
    ORDER BY rss_feeds.credibility_score DESC, rss_feeds.total_items_collected DESC;
$$;

-- 4. Check if the view was created properly
SELECT 
    schemaname,
    viewname,
    viewowner,
    definition
FROM pg_views 
WHERE schemaname = 'public' 
  AND viewname = 'active_rss_feeds';

-- 5. If you still get security definer warnings, we can just remove the view entirely
-- and use direct table queries instead. Run this if needed:
-- DROP VIEW IF EXISTS active_rss_feeds CASCADE;

SELECT 'View security issue fixed!' as message;