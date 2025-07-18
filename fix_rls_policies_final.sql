-- Final Fix for RLS Policies - Direct Approach
-- This script creates basic policies that will work regardless of column names

-- 1. Community Users - Simple public read + service access
DROP POLICY IF EXISTS "Public read access" ON community_users;
DROP POLICY IF EXISTS "Service role full access" ON community_users;
DROP POLICY IF EXISTS "Service role only access" ON community_users;

CREATE POLICY "Public read access" ON community_users FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON community_users FOR ALL USING (auth.role() = 'service_role');

-- 2. Discussions - Public read + authenticated insert + service access
DROP POLICY IF EXISTS "Public read access" ON discussions;
DROP POLICY IF EXISTS "Authenticated insert" ON discussions;
DROP POLICY IF EXISTS "Service role full access" ON discussions;
DROP POLICY IF EXISTS "Service role only access" ON discussions;

CREATE POLICY "Public read access" ON discussions FOR SELECT USING (true);
CREATE POLICY "Authenticated insert" ON discussions FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Service role full access" ON discussions FOR ALL USING (auth.role() = 'service_role');

-- 3. Notifications - Service role only (safest approach)
DROP POLICY IF EXISTS "Service role only access" ON notifications;
DROP POLICY IF EXISTS "Service role full access" ON notifications;

CREATE POLICY "Service role only access" ON notifications FOR ALL USING (auth.role() = 'service_role');

-- 4. User Profiles - Service role only (safest approach)
DROP POLICY IF EXISTS "Service role only access" ON user_profiles;
DROP POLICY IF EXISTS "Service role full access" ON user_profiles;

CREATE POLICY "Service role only access" ON user_profiles FOR ALL USING (auth.role() = 'service_role');

-- 5. Verify all policies are created
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE schemaname = 'public' 
  AND tablename IN ('community_users', 'discussions', 'notifications', 'user_profiles')
ORDER BY tablename, policyname;

-- 6. Check final RLS status
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
  AND tablename IN ('community_users', 'discussions', 'notifications', 'user_profiles')
ORDER BY tablename;

SELECT 'RLS policies created successfully!' as message;