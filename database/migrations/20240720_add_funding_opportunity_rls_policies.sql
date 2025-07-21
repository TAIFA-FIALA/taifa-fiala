-- RLS Policies for africa_intelligence_feed table
-- This script adds appropriate row-level security policies for the funding opportunities

-- Enable RLS on the table if not already enabled
ALTER TABLE public.africa_intelligence_feed ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Public read access" ON public.africa_intelligence_feed;
DROP POLICY IF EXISTS "Authenticated users can read" ON public.africa_intelligence_feed;
DROP POLICY IF EXISTS "Service role full access" ON public.africa_intelligence_feed;

-- Public read access for published funding opportunities
CREATE POLICY "Public read access" 
ON public.africa_intelligence_feed
FOR SELECT
USING (
    -- Only show active, non-expired opportunities to the public
    (status = 'active' OR status IS NULL) AND 
    (application_deadline IS NULL OR application_deadline >= CURRENT_DATE) AND
    is_active = TRUE
);

-- Authenticated users can read all opportunities including draft/expired ones
CREATE POLICY "Authenticated users can read" 
ON public.africa_intelligence_feed
FOR SELECT
TO authenticated
USING (true);

-- Service role has full access (for background jobs and admin functions)
CREATE POLICY "Service role full access" 
ON public.africa_intelligence_feed
FOR ALL
TO service_role
USING (true);

-- Admin users can perform all operations
CREATE POLICY "Admins can manage all funding opportunities"
ON public.africa_intelligence_feed
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM auth.users
        WHERE id = auth.uid() AND 
        (raw_user_meta_data->>'role' = 'admin' OR 
         raw_user_meta_data->>'role' = 'super_admin')
    )
);

-- Users with appropriate roles can update records
CREATE POLICY "Editors can update records"
ON public.africa_intelligence_feed
FOR UPDATE
USING (
    EXISTS (
        SELECT 1 FROM auth.users
        WHERE id = auth.uid() AND 
        (raw_user_meta_data->>'role' IN ('editor', 'admin', 'super_admin'))
    )
);

-- Add comments for documentation
COMMENT ON TABLE public.africa_intelligence_feed IS 'AI-powered intelligence feed collecting news, funding opportunities, policy updates, and technology developments across Africa';
COMMENT ON POLICY "Public read access" ON public.africa_intelligence_feed IS 'Allows public read access to active, non-expired funding opportunities';
COMMENT ON POLICY "Authenticated users can read" ON public.africa_intelligence_feed IS 'Allows authenticated users to read all opportunities, including drafts and expired ones';
COMMENT ON POLICY "Service role full access" ON public.africa_intelligence_feed IS 'Grants full access to the service role (background jobs, admin functions)';
COMMENT ON POLICY "Admins can manage all funding opportunities" ON public.africa_intelligence_feed IS 'Allows admin users to perform all operations on funding opportunities';
COMMENT ON POLICY "Editors can update records" ON public.africa_intelligence_feed IS 'Allows users with editor, admin, or super_admin roles to update records';

-- Notify that RLS policies were applied
DO $$
BEGIN
    RAISE NOTICE 'Successfully applied RLS policies to africa_intelligence_feed table';
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error applying RLS policies: %', SQLERRM;
END $$;
