-- Fix Missing RLS Policies for User-Specific Tables
-- This script adds policies for the tables that have RLS enabled but no policies

-- First, let's see what columns these tables actually have
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name IN ('applications', 'community_users', 'discussions', 'notifications', 'user_profiles')
ORDER BY table_name, ordinal_position;

-- Applications Policies
DO $$
BEGIN
    -- Check what columns exist in applications table
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'applications' AND column_name = 'user_id') THEN
        -- Has user_id column
        DROP POLICY IF EXISTS "Users can view own applications" ON applications;
        DROP POLICY IF EXISTS "Users can insert own applications" ON applications;
        DROP POLICY IF EXISTS "Users can update own applications" ON applications;
        DROP POLICY IF EXISTS "Service role full access" ON applications;
        
        CREATE POLICY "Users can view own applications" ON applications FOR SELECT USING (auth.uid() = user_id);
        CREATE POLICY "Users can insert own applications" ON applications FOR INSERT WITH CHECK (auth.uid() = user_id);
        CREATE POLICY "Users can update own applications" ON applications FOR UPDATE USING (auth.uid() = user_id);
        CREATE POLICY "Service role full access" ON applications FOR ALL USING (auth.role() = 'service_role');
        
        RAISE NOTICE 'Policies created for applications (using user_id)';
    ELSIF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'applications' AND column_name = 'submitted_by_user_id') THEN
        -- Has submitted_by_user_id column
        DROP POLICY IF EXISTS "Users can view own applications" ON applications;
        DROP POLICY IF EXISTS "Users can insert own applications" ON applications;
        DROP POLICY IF EXISTS "Users can update own applications" ON applications;
        DROP POLICY IF EXISTS "Service role full access" ON applications;
        
        CREATE POLICY "Users can view own applications" ON applications FOR SELECT USING (auth.uid() = submitted_by_user_id);
        CREATE POLICY "Users can insert own applications" ON applications FOR INSERT WITH CHECK (auth.uid() = submitted_by_user_id);
        CREATE POLICY "Users can update own applications" ON applications FOR UPDATE USING (auth.uid() = submitted_by_user_id);
        CREATE POLICY "Service role full access" ON applications FOR ALL USING (auth.role() = 'service_role');
        
        RAISE NOTICE 'Policies created for applications (using submitted_by_user_id)';
    ELSE
        -- No user identifier column found, create basic service-only policy
        DROP POLICY IF EXISTS "Service role only access" ON applications;
        CREATE POLICY "Service role only access" ON applications FOR ALL USING (auth.role() = 'service_role');
        
        RAISE NOTICE 'Service-only policy created for applications (no user column found)';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table applications does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for applications: %', SQLERRM;
END $$;

-- Community Users Policies
DO $$
BEGIN
    DROP POLICY IF EXISTS "Public profile access" ON community_users;
    DROP POLICY IF EXISTS "Users can update own profile" ON community_users;
    DROP POLICY IF EXISTS "Service role full access" ON community_users;
    
    CREATE POLICY "Public profile access" ON community_users FOR SELECT USING (true);
    
    -- Check for user identifier column
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'community_users' AND column_name = 'id') THEN
        CREATE POLICY "Users can update own profile" ON community_users FOR UPDATE USING (auth.uid() = id);
        RAISE NOTICE 'Policies created for community_users (using id)';
    ELSIF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'community_users' AND column_name = 'user_id') THEN
        CREATE POLICY "Users can update own profile" ON community_users FOR UPDATE USING (auth.uid() = user_id);
        RAISE NOTICE 'Policies created for community_users (using user_id)';
    ELSE
        RAISE NOTICE 'Policies created for community_users (no user-specific updates)';
    END IF;
    
    CREATE POLICY "Service role full access" ON community_users FOR ALL USING (auth.role() = 'service_role');
    
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table community_users does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for community_users: %', SQLERRM;
END $$;

-- Discussions Policies
DO $$
BEGIN
    DROP POLICY IF EXISTS "Public read access" ON discussions;
    DROP POLICY IF EXISTS "Authenticated users can create discussions" ON discussions;
    DROP POLICY IF EXISTS "Users can update own discussions" ON discussions;
    DROP POLICY IF EXISTS "Service role full access" ON discussions;
    
    CREATE POLICY "Public read access" ON discussions FOR SELECT USING (true);
    CREATE POLICY "Authenticated users can create discussions" ON discussions FOR INSERT WITH CHECK (auth.role() = 'authenticated');
    
    -- Check for creator column
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'discussions' AND column_name = 'created_by') THEN
        CREATE POLICY "Users can update own discussions" ON discussions FOR UPDATE USING (auth.uid() = created_by);
        RAISE NOTICE 'Policies created for discussions (using created_by)';
    ELSIF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'discussions' AND column_name = 'user_id') THEN
        CREATE POLICY "Users can update own discussions" ON discussions FOR UPDATE USING (auth.uid() = user_id);
        RAISE NOTICE 'Policies created for discussions (using user_id)';
    ELSE
        RAISE NOTICE 'Policies created for discussions (no user-specific updates)';
    END IF;
    
    CREATE POLICY "Service role full access" ON discussions FOR ALL USING (auth.role() = 'service_role');
    
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table discussions does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for discussions: %', SQLERRM;
END $$;

-- Notifications Policies
DO $$
BEGIN
    DROP POLICY IF EXISTS "Users can view own notifications" ON notifications;
    DROP POLICY IF EXISTS "Users can update own notifications" ON notifications;
    DROP POLICY IF EXISTS "Service role full access" ON notifications;
    
    -- Check for user identifier column
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'notifications' AND column_name = 'user_id') THEN
        CREATE POLICY "Users can view own notifications" ON notifications FOR SELECT USING (auth.uid() = user_id);
        CREATE POLICY "Users can update own notifications" ON notifications FOR UPDATE USING (auth.uid() = user_id);
        RAISE NOTICE 'Policies created for notifications (using user_id)';
    ELSIF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'notifications' AND column_name = 'recipient_id') THEN
        CREATE POLICY "Users can view own notifications" ON notifications FOR SELECT USING (auth.uid() = recipient_id);
        CREATE POLICY "Users can update own notifications" ON notifications FOR UPDATE USING (auth.uid() = recipient_id);
        RAISE NOTICE 'Policies created for notifications (using recipient_id)';
    ELSE
        -- No user identifier found, create service-only policy
        CREATE POLICY "Service role only access" ON notifications FOR ALL USING (auth.role() = 'service_role');
        RAISE NOTICE 'Service-only policy created for notifications (no user column found)';
    END IF;
    
    CREATE POLICY "Service role full access" ON notifications FOR ALL USING (auth.role() = 'service_role');
    
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table notifications does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for notifications: %', SQLERRM;
END $$;

-- User Profiles Policies
DO $$
BEGIN
    DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
    DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
    DROP POLICY IF EXISTS "Public basic profile access" ON user_profiles;
    DROP POLICY IF EXISTS "Service role full access" ON user_profiles;
    
    -- Check for user identifier column
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'user_id') THEN
        CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = user_id);
        CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = user_id);
        RAISE NOTICE 'Policies created for user_profiles (using user_id)';
    ELSIF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'id') THEN
        CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
        CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);
        RAISE NOTICE 'Policies created for user_profiles (using id)';
    ELSE
        -- No user identifier found, create service-only policy
        CREATE POLICY "Service role only access" ON user_profiles FOR ALL USING (auth.role() = 'service_role');
        RAISE NOTICE 'Service-only policy created for user_profiles (no user column found)';
    END IF;
    
    -- Check for public visibility column
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'is_public') THEN
        CREATE POLICY "Public basic profile access" ON user_profiles FOR SELECT USING (is_public = true);
        RAISE NOTICE 'Public profile access policy created';
    END IF;
    
    CREATE POLICY "Service role full access" ON user_profiles FOR ALL USING (auth.role() = 'service_role');
    
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table user_profiles does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for user_profiles: %', SQLERRM;
END $$;

-- Final success message
SELECT 'Missing RLS policies have been created!' as message;

-- Show updated policy status
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