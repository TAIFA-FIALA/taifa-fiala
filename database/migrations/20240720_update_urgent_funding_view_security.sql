-- Update views to use SECURITY INVOKER
-- This ensures views respect the permissions of the user executing the query

-- ==========================================
-- 1. Update urgent_funding_opportunities view
-- ==========================================
DROP VIEW IF EXISTS public.urgent_funding_opportunities;

CREATE OR REPLACE VIEW public.urgent_funding_opportunities 
WITH (security_invoker = true)
AS
SELECT 
    id,
    title,
    COALESCE(
        (SELECT name FROM organizations WHERE id = provider_organization_id LIMIT 1),
        'Unknown Organization'
    ) as organization_name,
    funding_type,
    CASE 
        WHEN funding_type = 'total_pool' THEN total_funding_pool::TEXT
        WHEN funding_type = 'per_project_exact' THEN exact_amount_per_project::TEXT
        WHEN funding_type = 'per_project_range' THEN 
            COALESCE(amount_min::TEXT, '') || ' - ' || COALESCE(amount_max::TEXT, '')
        WHEN amount_exact IS NOT NULL THEN amount_exact::TEXT
        WHEN amount_min IS NOT NULL AND amount_max IS NOT NULL THEN 
            COALESCE(amount_min::TEXT, '') || ' - ' || COALESCE(amount_max::TEXT, '')
        ELSE 'Amount not specified'
    END as funding_amount_display,
    application_deadline,
    urgency_level,
    days_until_deadline,
    application_deadline_type,
    gender_focused,
    youth_focused,
    collaboration_required,
    currency
FROM africa_intelligence_feed
WHERE (status IS NULL OR status != 'inactive')
  AND application_deadline >= CURRENT_DATE
  AND urgency_level IN ('urgent', 'moderate')
ORDER BY urgency_level = 'urgent' DESC, days_until_deadline ASC;

COMMENT ON VIEW public.urgent_funding_opportunities IS 'Shows urgent and moderate priority funding opportunities that are currently active and have not yet reached their deadline. Uses SECURITY INVOKER to respect row-level security policies.';

-- ==========================================
-- 2. Update active_rss_feeds view if it exists
-- ==========================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = 'active_rss_feeds') THEN
        DROP VIEW public.active_rss_feeds;
        
        CREATE VIEW public.active_rss_feeds 
        WITH (security_invoker = true)
        AS
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
        
        COMMENT ON VIEW public.active_rss_feeds IS 'Shows active RSS feeds ordered by credibility and collection metrics. Uses SECURITY INVOKER to respect row-level security policies.';
        RAISE NOTICE 'Updated active_rss_feeds view to use SECURITY INVOKER';
    ELSE
        RAISE NOTICE 'active_rss_feeds view does not exist, skipping';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error updating active_rss_feeds view: %', SQLERRM;
END $$;

-- ==========================================
-- 3. Update funding_opportunities_by_type view if it exists
-- ==========================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = 'funding_opportunities_by_type') THEN
        DROP VIEW public.funding_opportunities_by_type;
        
CREATE VIEW public.funding_opportunities_by_type 
        WITH (security_invoker = true)
        AS
        SELECT 
            funding_type,
            COUNT(*) as opportunity_count,
            AVG(CASE 
                WHEN funding_type = 'total_pool' THEN total_funding_pool
                WHEN funding_type = 'per_project_exact' THEN exact_amount_per_project
                WHEN funding_type = 'per_project_range' THEN (COALESCE(min_amount_per_project, 0) + COALESCE(max_amount_per_project, 0)) / 2
                WHEN amount_exact IS NOT NULL THEN amount_exact
                WHEN amount_min IS NOT NULL AND amount_max IS NOT NULL THEN (amount_min + amount_max) / 2
                ELSE NULL
            END) as avg_funding_amount,
            SUM(CASE 
                WHEN funding_type = 'total_pool' THEN total_funding_pool
                WHEN funding_type = 'per_project_exact' THEN exact_amount_per_project * COALESCE(estimated_project_count, 1)
                WHEN funding_type = 'per_project_range' THEN ((COALESCE(min_amount_per_project, 0) + COALESCE(max_amount_per_project, 0)) / 2) * COALESCE(estimated_project_count, 1)
                WHEN amount_exact IS NOT NULL THEN amount_exact
                WHEN amount_min IS NOT NULL AND amount_max IS NOT NULL THEN (amount_min + amount_max) / 2
                ELSE 0
            END) as total_funding_available
        FROM africa_intelligence_feed
        WHERE status IS NULL OR status != 'inactive'
        GROUP BY funding_type;
        
        COMMENT ON VIEW public.funding_opportunities_by_type IS 'Shows funding opportunities grouped by type with aggregated metrics. Uses SECURITY INVOKER to respect row-level security policies.';
        RAISE NOTICE 'Updated funding_opportunities_by_type view to use SECURITY INVOKER';
    ELSE
        RAISE NOTICE 'funding_opportunities_by_type view does not exist, skipping';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error updating funding_opportunities_by_type view: %', SQLERRM;
END $$;

-- ==========================================
-- Final notification
-- ==========================================
DO $$
BEGIN
    RAISE NOTICE 'Successfully updated all views to use SECURITY INVOKER';
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error in final notification: %', SQLERRM;
END $$;
