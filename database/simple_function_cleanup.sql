-- Simple Function Cleanup - Remove Unused Function and Fix Trigger
-- This is the cleanest approach

-- 1. Remove the unused get_active_rss_feeds function completely
DROP FUNCTION IF EXISTS get_active_rss_feeds();

-- 2. Fix the trigger function with proper search_path
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

-- 3. Verify only the trigger function remains and is properly configured
SELECT 
    proname as function_name,
    prosecdef as is_security_definer,
    proconfig as function_settings
FROM pg_proc 
WHERE proname = 'update_rss_feeds_updated_at'
  AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

-- 4. Verify the unused function is gone
SELECT 
    COUNT(*) as functions_remaining
FROM pg_proc 
WHERE proname = 'get_active_rss_feeds'
  AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

-- Should return 0 if the function is properly removed

SELECT 'Function cleanup complete - all search path warnings should be gone!' as message;