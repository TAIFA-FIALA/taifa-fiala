-- Simple Fix for Function Search Path Issues
-- This removes the unused function and fixes the trigger function

-- 1. Drop the unused get_active_rss_feeds function
DROP FUNCTION IF EXISTS get_active_rss_feeds();

-- 2. Fix the trigger function with proper search_path
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

-- 3. Verify the fixes
SELECT 
    proname as function_name,
    prosecdef as is_security_definer,
    proconfig as function_settings
FROM pg_proc 
WHERE proname = 'update_rss_feeds_updated_at'
  AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

SELECT 'Function search path warnings fixed!' as message;