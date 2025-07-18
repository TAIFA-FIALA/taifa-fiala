-- TAIFA-FIALA RLS Policies for Supabase SQL Editor
-- Copy and paste this script into Supabase SQL Editor
-- This script will only create policies for tables that exist

-- Helper function to check if table exists and enable RLS
DO $$
DECLARE
    table_name TEXT;
    tables_to_secure TEXT[] := ARRAY[
        'africa_intelligence_feed',
        'ai_domains',
        'announcements',
        'applications',
        'community_users',
        'discussions',
        'events',
        'funding_opportunities_backup',
        'funding_rounds',
        'funding_types',
        'geographic_scopes',
        'health_check',
        'impact_metrics',
        'investments',
        'notifications',
        'organizations',
        'partnerships',
        'performance_metrics',
        'publications',
        'raw_content',
        'research_projects',
        'resources',
        'scraping_queue',
        'scraping_queue_status',
        'scraping_results',
        'scraping_templates',
        'user_profiles'
    ];
BEGIN
    -- Enable RLS on existing tables
    FOREACH table_name IN ARRAY tables_to_secure
    LOOP
        BEGIN
            EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_name);
            RAISE NOTICE 'RLS enabled on table: %', table_name;
        EXCEPTION
            WHEN undefined_table THEN
                RAISE NOTICE 'Table % does not exist, skipping', table_name;
            WHEN OTHERS THEN
                RAISE NOTICE 'Error enabling RLS on %: %', table_name, SQLERRM;
        END;
    END LOOP;
END $$;

-- Core Intelligence Feed Policies
DO $$
BEGIN
    -- Drop existing policies if they exist
    DROP POLICY IF EXISTS "Public read access" ON africa_intelligence_feed;
    DROP POLICY IF EXISTS "Service role full access" ON africa_intelligence_feed;
    DROP POLICY IF EXISTS "Authenticated insert" ON africa_intelligence_feed;
    
    -- Create new policies
    CREATE POLICY "Public read access" ON africa_intelligence_feed FOR SELECT USING (true);
    CREATE POLICY "Service role full access" ON africa_intelligence_feed FOR ALL USING (auth.role() = 'service_role');
    CREATE POLICY "Authenticated insert" ON africa_intelligence_feed FOR INSERT WITH CHECK (auth.role() = 'authenticated');
    
    RAISE NOTICE 'Policies created for africa_intelligence_feed';
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table africa_intelligence_feed does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for africa_intelligence_feed: %', SQLERRM;
END $$;

-- AI Domains Policies
DO $$
BEGIN
    DROP POLICY IF EXISTS "Public read access" ON ai_domains;
    DROP POLICY IF EXISTS "Service role full access" ON ai_domains;
    
    CREATE POLICY "Public read access" ON ai_domains FOR SELECT USING (true);
    CREATE POLICY "Service role full access" ON ai_domains FOR ALL USING (auth.role() = 'service_role');
    
    RAISE NOTICE 'Policies created for ai_domains';
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table ai_domains does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for ai_domains: %', SQLERRM;
END $$;

-- Organizations Policies
DO $$
BEGIN
    DROP POLICY IF EXISTS "Public read access" ON organizations;
    DROP POLICY IF EXISTS "Service role full access" ON organizations;
    
    CREATE POLICY "Public read access" ON organizations FOR SELECT USING (true);
    CREATE POLICY "Service role full access" ON organizations FOR ALL USING (auth.role() = 'service_role');
    
    RAISE NOTICE 'Policies created for organizations';
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table organizations does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for organizations: %', SQLERRM;
END $$;

-- Health Check Policies
DO $$
BEGIN
    DROP POLICY IF EXISTS "Public read access" ON health_check;
    DROP POLICY IF EXISTS "Service role full access" ON health_check;
    
    CREATE POLICY "Public read access" ON health_check FOR SELECT USING (true);
    CREATE POLICY "Service role full access" ON health_check FOR ALL USING (auth.role() = 'service_role');
    
    RAISE NOTICE 'Policies created for health_check';
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table health_check does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for health_check: %', SQLERRM;
END $$;

-- Funding Types Policies
DO $$
BEGIN
    DROP POLICY IF EXISTS "Public read access" ON funding_types;
    DROP POLICY IF EXISTS "Service role full access" ON funding_types;
    
    CREATE POLICY "Public read access" ON funding_types FOR SELECT USING (true);
    CREATE POLICY "Service role full access" ON funding_types FOR ALL USING (auth.role() = 'service_role');
    
    RAISE NOTICE 'Policies created for funding_types';
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table funding_types does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for funding_types: %', SQLERRM;
END $$;

-- Geographic Scopes Policies
DO $$
BEGIN
    DROP POLICY IF EXISTS "Public read access" ON geographic_scopes;
    DROP POLICY IF EXISTS "Service role full access" ON geographic_scopes;
    
    CREATE POLICY "Public read access" ON geographic_scopes FOR SELECT USING (true);
    CREATE POLICY "Service role full access" ON geographic_scopes FOR ALL USING (auth.role() = 'service_role');
    
    RAISE NOTICE 'Policies created for geographic_scopes';
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table geographic_scopes does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for geographic_scopes: %', SQLERRM;
END $$;

-- Community Users Policies
DO $$
BEGIN
    DROP POLICY IF EXISTS "Public profile access" ON community_users;
    DROP POLICY IF EXISTS "Users can update own profile" ON community_users;
    DROP POLICY IF EXISTS "Service role full access" ON community_users;
    
    CREATE POLICY "Public profile access" ON community_users FOR SELECT USING (true);
    CREATE POLICY "Users can update own profile" ON community_users FOR UPDATE USING (auth.uid() = id);
    CREATE POLICY "Service role full access" ON community_users FOR ALL USING (auth.role() = 'service_role');
    
    RAISE NOTICE 'Policies created for community_users';
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table community_users does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for community_users: %', SQLERRM;
END $$;

-- Applications Policies (User-specific)
DO $$
BEGIN
    DROP POLICY IF EXISTS "Users can view own applications" ON applications;
    DROP POLICY IF EXISTS "Users can insert own applications" ON applications;
    DROP POLICY IF EXISTS "Users can update own applications" ON applications;
    DROP POLICY IF EXISTS "Service role full access" ON applications;
    
    CREATE POLICY "Users can view own applications" ON applications FOR SELECT USING (auth.uid() = user_id);
    CREATE POLICY "Users can insert own applications" ON applications FOR INSERT WITH CHECK (auth.uid() = user_id);
    CREATE POLICY "Users can update own applications" ON applications FOR UPDATE USING (auth.uid() = user_id);
    CREATE POLICY "Service role full access" ON applications FOR ALL USING (auth.role() = 'service_role');
    
    RAISE NOTICE 'Policies created for applications';
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table applications does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for applications: %', SQLERRM;
END $$;

-- Notifications Policies (User-specific)
DO $$
BEGIN
    DROP POLICY IF EXISTS "Users can view own notifications" ON notifications;
    DROP POLICY IF EXISTS "Users can update own notifications" ON notifications;
    DROP POLICY IF EXISTS "Service role full access" ON notifications;
    
    CREATE POLICY "Users can view own notifications" ON notifications FOR SELECT USING (auth.uid() = user_id);
    CREATE POLICY "Users can update own notifications" ON notifications FOR UPDATE USING (auth.uid() = user_id);
    CREATE POLICY "Service role full access" ON notifications FOR ALL USING (auth.role() = 'service_role');
    
    RAISE NOTICE 'Policies created for notifications';
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table notifications does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for notifications: %', SQLERRM;
END $$;

-- User Profiles Policies (User-specific with public option)
DO $$
BEGIN
    DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
    DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
    DROP POLICY IF EXISTS "Public basic profile access" ON user_profiles;
    DROP POLICY IF EXISTS "Service role full access" ON user_profiles;
    
    CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = user_id);
    CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = user_id);
    CREATE POLICY "Public basic profile access" ON user_profiles FOR SELECT USING (is_public = true);
    CREATE POLICY "Service role full access" ON user_profiles FOR ALL USING (auth.role() = 'service_role');
    
    RAISE NOTICE 'Policies created for user_profiles';
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table user_profiles does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for user_profiles: %', SQLERRM;
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
    CREATE POLICY "Users can update own discussions" ON discussions FOR UPDATE USING (auth.uid() = created_by);
    CREATE POLICY "Service role full access" ON discussions FOR ALL USING (auth.role() = 'service_role');
    
    RAISE NOTICE 'Policies created for discussions';
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'Table discussions does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating policies for discussions: %', SQLERRM;
END $$;

-- Service-only tables (scraping, raw content, etc.)
DO $$
DECLARE
    service_tables TEXT[] := ARRAY[
        'raw_content',
        'scraping_queue',
        'scraping_queue_status',
        'scraping_results',
        'scraping_templates',
        'funding_opportunities_backup'
    ];
    table_name TEXT;
BEGIN
    FOREACH table_name IN ARRAY service_tables
    LOOP
        BEGIN
            EXECUTE format('DROP POLICY IF EXISTS "Service role only access" ON %I', table_name);
            EXECUTE format('CREATE POLICY "Service role only access" ON %I FOR ALL USING (auth.role() = ''service_role'')', table_name);
            RAISE NOTICE 'Service-only policy created for %', table_name;
        EXCEPTION
            WHEN undefined_table THEN
                RAISE NOTICE 'Table % does not exist', table_name;
            WHEN OTHERS THEN
                RAISE NOTICE 'Error creating service policy for %: %', table_name, SQLERRM;
        END;
    END LOOP;
END $$;

-- Public read tables (announcements, events, etc.)
DO $$
DECLARE
    public_tables TEXT[] := ARRAY[
        'announcements',
        'events',
        'funding_rounds',
        'impact_metrics',
        'investments',
        'partnerships',
        'performance_metrics',
        'publications',
        'research_projects',
        'resources'
    ];
    table_name TEXT;
BEGIN
    FOREACH table_name IN ARRAY public_tables
    LOOP
        BEGIN
            EXECUTE format('DROP POLICY IF EXISTS "Public read access" ON %I', table_name);
            EXECUTE format('DROP POLICY IF EXISTS "Service role full access" ON %I', table_name);
            EXECUTE format('CREATE POLICY "Public read access" ON %I FOR SELECT USING (true)', table_name);
            EXECUTE format('CREATE POLICY "Service role full access" ON %I FOR ALL USING (auth.role() = ''service_role'')', table_name);
            RAISE NOTICE 'Public read policies created for %', table_name;
        EXCEPTION
            WHEN undefined_table THEN
                RAISE NOTICE 'Table % does not exist', table_name;
            WHEN OTHERS THEN
                RAISE NOTICE 'Error creating public policies for %: %', table_name, SQLERRM;
        END;
    END LOOP;
END $$;

-- Final success message
SELECT 'RLS policies created successfully for existing tables!' as message;

-- Show which tables have RLS enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity as "RLS Enabled"
FROM pg_tables 
WHERE schemaname = 'public' 
  AND rowsecurity = true
ORDER BY tablename;