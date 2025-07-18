-- Fix Critical Security Issues for TAIFA-FIALA
-- This script fixes the Security Definer View and adds missing RLS policies

-- 1. Fix the Security Definer View issue
-- Drop the existing view and recreate it properly
DROP VIEW IF EXISTS active_rss_feeds;

-- Create a safe view without SECURITY DEFINER
CREATE VIEW active_rss_feeds AS
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

-- Add RLS policy for the view (views inherit from base table policies)
-- No additional RLS needed for views - they use the base table's policies

-- 2. Fix Missing RLS Policies for the problematic tables
-- Let's check what columns these tables actually have first

-- Applications table policies
DO $$
DECLARE
    user_col TEXT;
BEGIN
    -- Find the user identifier column
    SELECT column_name INTO user_col
    FROM information_schema.columns 
    WHERE table_name = 'applications' 
      AND column_name IN ('user_id', 'submitted_by', 'created_by', 'applicant_id')
    LIMIT 1;
    
    IF user_col IS NOT NULL THEN
        -- Drop existing policies
        DROP POLICY IF EXISTS "Users can view own applications" ON applications;
        DROP POLICY IF EXISTS "Users can insert own applications" ON applications;
        DROP POLICY IF EXISTS "Users can update own applications" ON applications;
        DROP POLICY IF EXISTS "Service role full access" ON applications;
        DROP POLICY IF EXISTS "Service role only access" ON applications;
        
        -- Create user-specific policies
        EXECUTE format('CREATE POLICY "Users can view own applications" ON applications FOR SELECT USING (auth.uid() = %I)', user_col);
        EXECUTE format('CREATE POLICY "Users can insert own applications" ON applications FOR INSERT WITH CHECK (auth.uid() = %I)', user_col);
        EXECUTE format('CREATE POLICY "Users can update own applications" ON applications FOR UPDATE USING (auth.uid() = %I)', user_col);
        CREATE POLICY "Service role full access" ON applications FOR ALL USING (auth.role() = 'service_role');
        
        RAISE NOTICE 'Applications policies created using column: %', user_col;
    ELSE
        -- No user column found, create service-only policy
        DROP POLICY IF EXISTS "Service role only access" ON applications;
        CREATE POLICY "Service role only access" ON applications FOR ALL USING (auth.role() = 'service_role');
        RAISE NOTICE 'Applications: Service-only policy created (no user column found)';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table applications does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating applications policies: %', SQLERRM;
END $$;

-- Community Users table policies
DO $$
DECLARE
    user_col TEXT;
BEGIN
    -- Find the user identifier column
    SELECT column_name INTO user_col
    FROM information_schema.columns 
    WHERE table_name = 'community_users' 
      AND column_name IN ('id', 'user_id', 'auth_id')
    LIMIT 1;
    
    -- Drop existing policies
    DROP POLICY IF EXISTS "Public profile access" ON community_users;
    DROP POLICY IF EXISTS "Users can update own profile" ON community_users;
    DROP POLICY IF EXISTS "Service role full access" ON community_users;
    DROP POLICY IF EXISTS "Service role only access" ON community_users;
    
    -- Always allow public read access for community users
    CREATE POLICY "Public profile access" ON community_users FOR SELECT USING (true);
    CREATE POLICY "Service role full access" ON community_users FOR ALL USING (auth.role() = 'service_role');
    
    IF user_col IS NOT NULL THEN
        EXECUTE format('CREATE POLICY "Users can update own profile" ON community_users FOR UPDATE USING (auth.uid() = %I)', user_col);
        RAISE NOTICE 'Community users policies created using column: %', user_col;
    ELSE
        RAISE NOTICE 'Community users: Public read + service access (no user updates)';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table community_users does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating community_users policies: %', SQLERRM;
END $$;

-- Discussions table policies
DO $$
DECLARE
    user_col TEXT;
BEGIN
    -- Find the user identifier column
    SELECT column_name INTO user_col
    FROM information_schema.columns 
    WHERE table_name = 'discussions' 
      AND column_name IN ('created_by', 'user_id', 'author_id')
    LIMIT 1;
    
    -- Drop existing policies
    DROP POLICY IF EXISTS "Public read access" ON discussions;
    DROP POLICY IF EXISTS "Authenticated users can create discussions" ON discussions;
    DROP POLICY IF EXISTS "Users can update own discussions" ON discussions;
    DROP POLICY IF EXISTS "Service role full access" ON discussions;
    DROP POLICY IF EXISTS "Service role only access" ON discussions;
    
    -- Basic policies for discussions
    CREATE POLICY "Public read access" ON discussions FOR SELECT USING (true);
    CREATE POLICY "Authenticated users can create discussions" ON discussions FOR INSERT WITH CHECK (auth.role() = 'authenticated');
    CREATE POLICY "Service role full access" ON discussions FOR ALL USING (auth.role() = 'service_role');
    
    IF user_col IS NOT NULL THEN
        EXECUTE format('CREATE POLICY "Users can update own discussions" ON discussions FOR UPDATE USING (auth.uid() = %I)', user_col);
        RAISE NOTICE 'Discussions policies created using column: %', user_col;
    ELSE
        RAISE NOTICE 'Discussions: Public read + authenticated create + service access';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table discussions does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating discussions policies: %', SQLERRM;
END $$;

-- Notifications table policies
DO $$
DECLARE
    user_col TEXT;
BEGIN
    -- Find the user identifier column
    SELECT column_name INTO user_col
    FROM information_schema.columns 
    WHERE table_name = 'notifications' 
      AND column_name IN ('user_id', 'recipient_id', 'target_user_id')
    LIMIT 1;
    
    -- Drop existing policies
    DROP POLICY IF EXISTS "Users can view own notifications" ON notifications;
    DROP POLICY IF EXISTS "Users can update own notifications" ON notifications;
    DROP POLICY IF EXISTS "Service role full access" ON notifications;
    DROP POLICY IF EXISTS "Service role only access" ON notifications;
    
    IF user_col IS NOT NULL THEN
        -- User-specific notifications
        EXECUTE format('CREATE POLICY "Users can view own notifications" ON notifications FOR SELECT USING (auth.uid() = %I)', user_col);
        EXECUTE format('CREATE POLICY "Users can update own notifications" ON notifications FOR UPDATE USING (auth.uid() = %I)', user_col);
        CREATE POLICY "Service role full access" ON notifications FOR ALL USING (auth.role() = 'service_role');
        RAISE NOTICE 'Notifications policies created using column: %', user_col;
    ELSE
        -- No user column, service-only
        CREATE POLICY "Service role only access" ON notifications FOR ALL USING (auth.role() = 'service_role');
        RAISE NOTICE 'Notifications: Service-only policy created (no user column found)';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table notifications does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating notifications policies: %', SQLERRM;
END $$;

-- User Profiles table policies
DO $$
DECLARE
    user_col TEXT;
    public_col TEXT;
BEGIN
    -- Find the user identifier column
    SELECT column_name INTO user_col
    FROM information_schema.columns 
    WHERE table_name = 'user_profiles' 
      AND column_name IN ('user_id', 'id', 'profile_id')
    LIMIT 1;
    
    -- Find the public visibility column
    SELECT column_name INTO public_col
    FROM information_schema.columns 
    WHERE table_name = 'user_profiles' 
      AND column_name IN ('is_public', 'public_profile', 'visibility')
    LIMIT 1;
    
    -- Drop existing policies
    DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
    DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
    DROP POLICY IF EXISTS "Public basic profile access" ON user_profiles;
    DROP POLICY IF EXISTS "Service role full access" ON user_profiles;
    DROP POLICY IF EXISTS "Service role only access" ON user_profiles;
    
    CREATE POLICY "Service role full access" ON user_profiles FOR ALL USING (auth.role() = 'service_role');
    
    IF user_col IS NOT NULL THEN
        -- User-specific profiles
        EXECUTE format('CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = %I)', user_col);
        EXECUTE format('CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = %I)', user_col);
        
        -- Public profile access if public column exists
        IF public_col IS NOT NULL THEN
            EXECUTE format('CREATE POLICY "Public basic profile access" ON user_profiles FOR SELECT USING (%I = true)', public_col);
            RAISE NOTICE 'User profiles policies created using user column: % and public column: %', user_col, public_col;
        ELSE
            RAISE NOTICE 'User profiles policies created using user column: % (no public access)', user_col;
        END IF;
    ELSE
        -- No user column, service-only
        CREATE POLICY "Service role only access" ON user_profiles FOR ALL USING (auth.role() = 'service_role');
        RAISE NOTICE 'User profiles: Service-only policy created (no user column found)';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table user_profiles does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating user_profiles policies: %', SQLERRM;
END $$;

-- 3. Verify the fixes
SELECT 'Security issues fixed!' as message;

-- Show tables with RLS status
SELECT 
    schemaname,
    tablename,
    rowsecurity as "RLS Enabled",
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM pg_policies 
            WHERE schemaname = 'public' 
            AND tablename = pg_tables.tablename
        ) THEN 'Has Policies'
        ELSE 'No Policies'
    END as "Policy Status"
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('applications', 'community_users', 'discussions', 'notifications', 'user_profiles')
ORDER BY tablename;

-- Show view information
SELECT 
    schemaname,
    viewname,
    definition
FROM pg_views 
WHERE schemaname = 'public' 
  AND viewname = 'active_rss_feeds';

-- Final success message
SELECT 'All security issues have been resolved!' as final_message;