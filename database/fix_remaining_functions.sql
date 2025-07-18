-- Fix Remaining Function Search Path Issues
-- This script fixes the search_path warnings for both functions

-- 1. Fix the update_rss_feeds_updated_at trigger function
CREATE OR REPLACE FUNCTION update_rss_feeds_updated_at()
RETURNS TRIGGER 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = 'public'
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

-- 2. Fix or remove the get_active_rss_feeds function
-- Option A: Fix it with proper search_path
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
    FROM public.rss_feeds
    WHERE is_active = true
    ORDER BY credibility_score DESC, total_items_collected DESC;
$$;

-- Option B: If you don't need the function, just drop it
-- DROP FUNCTION IF EXISTS get_active_rss_feeds();

-- 3. Verify the functions are fixed
SELECT 
    proname as function_name,
    prosecdef as is_security_definer,
    proconfig as function_settings
FROM pg_proc 
WHERE proname IN ('update_rss_feeds_updated_at', 'get_active_rss_feeds')
  AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

SELECT 'Function search path warnings fixed!' as message;