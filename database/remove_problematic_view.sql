-- Remove Problematic View Completely
-- This script removes the security definer view and replaces it with direct table access

-- 1. Drop the problematic view completely
DROP VIEW IF EXISTS active_rss_feeds CASCADE;

-- 2. Don't create a replacement view - just use direct table queries
-- This eliminates any security definer issues entirely

-- 3. If you need to query active feeds, use this query instead:
/*
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
*/

-- 4. Verify the view is gone
SELECT 
    COUNT(*) as view_count
FROM pg_views 
WHERE schemaname = 'public' 
  AND viewname = 'active_rss_feeds';

-- If count is 0, the view is successfully removed

SELECT 'Problematic view removed successfully!' as message;