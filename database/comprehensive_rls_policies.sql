-- TAIFA-FIALA Comprehensive RLS Policies
-- This script creates Row Level Security policies for all tables
-- Execute this in Supabase SQL Editor or via psql

-- Enable RLS on all tables
ALTER TABLE africa_intelligence_feed ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_domains ENABLE ROW LEVEL SECURITY;
ALTER TABLE announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE discussions ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE funding_opportunities_backup ENABLE ROW LEVEL SECURITY;
ALTER TABLE funding_rounds ENABLE ROW LEVEL SECURITY;
ALTER TABLE funding_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE geographic_scopes ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_check ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE investments ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE partnerships ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE publications ENABLE ROW LEVEL SECURITY;
ALTER TABLE raw_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_queue_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies (if any)
DROP POLICY IF EXISTS "Public read access" ON africa_intelligence_feed;
DROP POLICY IF EXISTS "Service role full access" ON africa_intelligence_feed;
DROP POLICY IF EXISTS "Authenticated insert" ON africa_intelligence_feed;

-- Africa Intelligence Feed Policies
CREATE POLICY "Public read access" ON africa_intelligence_feed FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON africa_intelligence_feed FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Authenticated insert" ON africa_intelligence_feed FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- AI Domains Policies
DROP POLICY IF EXISTS "Public read access" ON ai_domains;
DROP POLICY IF EXISTS "Service role full access" ON ai_domains;
CREATE POLICY "Public read access" ON ai_domains FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON ai_domains FOR ALL USING (auth.role() = 'service_role');

-- Announcements Policies
DROP POLICY IF EXISTS "Public read access" ON announcements;
DROP POLICY IF EXISTS "Service role full access" ON announcements;
CREATE POLICY "Public read access" ON announcements FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON announcements FOR ALL USING (auth.role() = 'service_role');

-- Applications Policies (User-specific)
DROP POLICY IF EXISTS "Users can view own applications" ON applications;
DROP POLICY IF EXISTS "Users can insert own applications" ON applications;
DROP POLICY IF EXISTS "Users can update own applications" ON applications;
DROP POLICY IF EXISTS "Service role full access" ON applications;
CREATE POLICY "Users can view own applications" ON applications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own applications" ON applications FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own applications" ON applications FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Service role full access" ON applications FOR ALL USING (auth.role() = 'service_role');

-- Community Users Policies
DROP POLICY IF EXISTS "Public profile access" ON community_users;
DROP POLICY IF EXISTS "Users can update own profile" ON community_users;
DROP POLICY IF EXISTS "Service role full access" ON community_users;
CREATE POLICY "Public profile access" ON community_users FOR SELECT USING (true);
CREATE POLICY "Users can update own profile" ON community_users FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Service role full access" ON community_users FOR ALL USING (auth.role() = 'service_role');

-- Discussions Policies
DROP POLICY IF EXISTS "Public read access" ON discussions;
DROP POLICY IF EXISTS "Authenticated users can create discussions" ON discussions;
DROP POLICY IF EXISTS "Users can update own discussions" ON discussions;
DROP POLICY IF EXISTS "Service role full access" ON discussions;
CREATE POLICY "Public read access" ON discussions FOR SELECT USING (true);
CREATE POLICY "Authenticated users can create discussions" ON discussions FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update own discussions" ON discussions FOR UPDATE USING (auth.uid() = created_by);
CREATE POLICY "Service role full access" ON discussions FOR ALL USING (auth.role() = 'service_role');

-- Events Policies
DROP POLICY IF EXISTS "Public read access" ON events;
DROP POLICY IF EXISTS "Service role full access" ON events;
CREATE POLICY "Public read access" ON events FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON events FOR ALL USING (auth.role() = 'service_role');

-- Funding Opportunities Backup Policies (Service only)
DROP POLICY IF EXISTS "Service role only access" ON funding_opportunities_backup;
CREATE POLICY "Service role only access" ON funding_opportunities_backup FOR ALL USING (auth.role() = 'service_role');

-- Funding Rounds Policies
DROP POLICY IF EXISTS "Public read access" ON funding_rounds;
DROP POLICY IF EXISTS "Service role full access" ON funding_rounds;
CREATE POLICY "Public read access" ON funding_rounds FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON funding_rounds FOR ALL USING (auth.role() = 'service_role');

-- Funding Types Policies
DROP POLICY IF EXISTS "Public read access" ON funding_types;
DROP POLICY IF EXISTS "Service role full access" ON funding_types;
CREATE POLICY "Public read access" ON funding_types FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON funding_types FOR ALL USING (auth.role() = 'service_role');

-- Geographic Scopes Policies
DROP POLICY IF EXISTS "Public read access" ON geographic_scopes;
DROP POLICY IF EXISTS "Service role full access" ON geographic_scopes;
CREATE POLICY "Public read access" ON geographic_scopes FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON geographic_scopes FOR ALL USING (auth.role() = 'service_role');

-- Health Check Policies
DROP POLICY IF EXISTS "Public read access" ON health_check;
DROP POLICY IF EXISTS "Service role full access" ON health_check;
CREATE POLICY "Public read access" ON health_check FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON health_check FOR ALL USING (auth.role() = 'service_role');

-- Impact Metrics Policies
DROP POLICY IF EXISTS "Public read access" ON impact_metrics;
DROP POLICY IF EXISTS "Service role full access" ON impact_metrics;
CREATE POLICY "Public read access" ON impact_metrics FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON impact_metrics FOR ALL USING (auth.role() = 'service_role');

-- Investments Policies
DROP POLICY IF EXISTS "Public read access" ON investments;
DROP POLICY IF EXISTS "Service role full access" ON investments;
CREATE POLICY "Public read access" ON investments FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON investments FOR ALL USING (auth.role() = 'service_role');

-- Notifications Policies (User-specific)
DROP POLICY IF EXISTS "Users can view own notifications" ON notifications;
DROP POLICY IF EXISTS "Users can update own notifications" ON notifications;
DROP POLICY IF EXISTS "Service role full access" ON notifications;
CREATE POLICY "Users can view own notifications" ON notifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own notifications" ON notifications FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Service role full access" ON notifications FOR ALL USING (auth.role() = 'service_role');

-- Organizations Policies
DROP POLICY IF EXISTS "Public read access" ON organizations;
DROP POLICY IF EXISTS "Service role full access" ON organizations;
CREATE POLICY "Public read access" ON organizations FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON organizations FOR ALL USING (auth.role() = 'service_role');

-- Partnerships Policies
DROP POLICY IF EXISTS "Public read access" ON partnerships;
DROP POLICY IF EXISTS "Service role full access" ON partnerships;
CREATE POLICY "Public read access" ON partnerships FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON partnerships FOR ALL USING (auth.role() = 'service_role');

-- Performance Metrics Policies
DROP POLICY IF EXISTS "Public read access" ON performance_metrics;
DROP POLICY IF EXISTS "Service role full access" ON performance_metrics;
CREATE POLICY "Public read access" ON performance_metrics FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON performance_metrics FOR ALL USING (auth.role() = 'service_role');

-- Publications Policies
DROP POLICY IF EXISTS "Public read access" ON publications;
DROP POLICY IF EXISTS "Service role full access" ON publications;
CREATE POLICY "Public read access" ON publications FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON publications FOR ALL USING (auth.role() = 'service_role');

-- Raw Content Policies (Service only)
DROP POLICY IF EXISTS "Service role only access" ON raw_content;
CREATE POLICY "Service role only access" ON raw_content FOR ALL USING (auth.role() = 'service_role');

-- Research Projects Policies
DROP POLICY IF EXISTS "Public read access" ON research_projects;
DROP POLICY IF EXISTS "Service role full access" ON research_projects;
CREATE POLICY "Public read access" ON research_projects FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON research_projects FOR ALL USING (auth.role() = 'service_role');

-- Resources Policies
DROP POLICY IF EXISTS "Public read access" ON resources;
DROP POLICY IF EXISTS "Service role full access" ON resources;
CREATE POLICY "Public read access" ON resources FOR SELECT USING (true);
CREATE POLICY "Service role full access" ON resources FOR ALL USING (auth.role() = 'service_role');

-- Scraping Queue Policies (Service only)
DROP POLICY IF EXISTS "Service role only access" ON scraping_queue;
CREATE POLICY "Service role only access" ON scraping_queue FOR ALL USING (auth.role() = 'service_role');

-- Scraping Queue Status Policies (Service only)
DROP POLICY IF EXISTS "Service role only access" ON scraping_queue_status;
CREATE POLICY "Service role only access" ON scraping_queue_status FOR ALL USING (auth.role() = 'service_role');

-- Scraping Results Policies (Service only)
DROP POLICY IF EXISTS "Service role only access" ON scraping_results;
CREATE POLICY "Service role only access" ON scraping_results FOR ALL USING (auth.role() = 'service_role');

-- Scraping Templates Policies (Service only)
DROP POLICY IF EXISTS "Service role only access" ON scraping_templates;
CREATE POLICY "Service role only access" ON scraping_templates FOR ALL USING (auth.role() = 'service_role');

-- User Profiles Policies (User-specific with public option)
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Public basic profile access" ON user_profiles;
DROP POLICY IF EXISTS "Service role full access" ON user_profiles;
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Public basic profile access" ON user_profiles FOR SELECT USING (is_public = true);
CREATE POLICY "Service role full access" ON user_profiles FOR ALL USING (auth.role() = 'service_role');

-- Success message
SELECT 'Comprehensive RLS policies created successfully!' as message;

-- Summary of security model:
-- 1. Public tables: Read access for all users (intelligence feed, organizations, events, etc.)
-- 2. User-specific tables: Users can only access their own data (applications, notifications, profiles)
-- 3. Service tables: Only service role can access (scraping queues, raw content, backups)
-- 4. Community tables: Public read, authenticated write (discussions)
-- 5. Admin/System tables: Service role only access