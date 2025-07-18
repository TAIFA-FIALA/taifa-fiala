-- Fix Function Search Path Security Issues
-- This script fixes the search_path warnings for better security

-- 1. Fix the update_rss_feeds_updated_at function
CREATE OR REPLACE FUNCTION update_rss_feeds_updated_at()
RETURNS TRIGGER 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

-- 2. Fix the get_active_rss_feeds function (if it still exists)
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
SET search_path = 'public'
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
    FROM public.rss_feeds
    WHERE rss_feeds.is_active = true
    ORDER BY rss_feeds.credibility_score DESC, rss_feeds.total_items_collected DESC;
$$;

-- 3. Alternative: If you don't need the get_active_rss_feeds function, just drop it
-- DROP FUNCTION IF EXISTS get_active_rss_feeds();

-- 4. Verify the functions are fixed
SELECT 
    proname as function_name,
    prosecdef as is_security_definer,
    proconfig as function_settings
FROM pg_proc 
WHERE proname IN ('update_rss_feeds_updated_at', 'get_active_rss_feeds')
  AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

SELECT 'Function search path issues fixed!' as message;