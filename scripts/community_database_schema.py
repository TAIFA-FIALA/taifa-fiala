"""
TAIFA-FIALA Community Features Implementation Plan
Technical roadmap for community engagement capabilities
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum

# =======================================================
# PHASE 1: COMMUNITY INFRASTRUCTURE (IMMEDIATE)
# =======================================================

class UserRole(Enum):
    VISITOR = "visitor"          # Read-only access
    CONTRIBUTOR = "contributor"   # Can submit content
    VALIDATOR = "validator"      # Can approve/reject submissions
    MODERATOR = "moderator"      # Can moderate discussions
    AMBASSADOR = "ambassador"    # Regional community lead
    ADMIN = "admin"             # Platform administration

class ContributionType(Enum):
    FUNDING_OPPORTUNITY = "funding_opportunity"
    TRANSLATION_IMPROVEMENT = "translation_improvement"
    CONTENT_VALIDATION = "content_validation"
    SUCCESS_STORY = "success_story"
    BEST_PRACTICE = "best_practice"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"

class ContributionStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

# =======================================================
# DATABASE SCHEMA EXTENSIONS
# =======================================================

community_schema_sql = """
-- User accounts and community profiles
CREATE TABLE IF NOT EXISTS community_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(20) DEFAULT 'visitor',
    country VARCHAR(100),
    organization VARCHAR(200),
    expertise_areas TEXT[], -- AI domains of expertise
    preferred_language VARCHAR(5) DEFAULT 'en',
    
    -- Community stats
    contribution_count INTEGER DEFAULT 0,
    validation_count INTEGER DEFAULT 0,
    reputation_score INTEGER DEFAULT 0,
    badges TEXT[], -- Array of earned badges
    
    -- Profile settings
    is_active BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    profile_public BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional profile data
    bio TEXT,
    website VARCHAR(500),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500)
);

-- Community contributions tracking
CREATE TABLE IF NOT EXISTS community_contributions (
    id SERIAL PRIMARY KEY,
    contributor_id INTEGER REFERENCES community_users(id),
    type VARCHAR(50) NOT NULL, -- ContributionType enum
    status VARCHAR(20) DEFAULT 'submitted',
    
    -- Content reference
    content_table VARCHAR(50), -- Which table the contribution relates to
    content_id INTEGER, -- ID in that table (nullable for new submissions)
    
    -- Submission data
    submission_data JSONB NOT NULL, -- The actual submitted content
    original_content JSONB, -- Original content (for improvements)
    
    -- Review process
    review_notes TEXT,
    reviewer_id INTEGER REFERENCES community_users(id),
    review_deadline TIMESTAMP,
    
    -- Quality metrics
    community_votes INTEGER DEFAULT 0,
    quality_score FLOAT DEFAULT 0.0,
    validation_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Peer review and validation system
CREATE TABLE IF NOT EXISTS contribution_reviews (
    id SERIAL PRIMARY KEY,
    contribution_id INTEGER REFERENCES community_contributions(id),
    reviewer_id INTEGER REFERENCES community_users(id),
    
    -- Review details
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_type VARCHAR(20), -- 'validation', 'quality', 'translation'
    comments TEXT,
    decision VARCHAR(20), -- 'approve', 'reject', 'needs_revision'
    
    -- Review categories
    accuracy_score INTEGER CHECK (accuracy_score >= 1 AND accuracy_score <= 5),
    relevance_score INTEGER CHECK (relevance_score >= 1 AND relevance_score <= 5),
    completeness_score INTEGER CHECK (completeness_score >= 1 AND completeness_score <= 5),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Community badges and achievements
CREATE TABLE IF NOT EXISTS community_badges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50), -- emoji or icon identifier
    category VARCHAR(50), -- 'contribution', 'validation', 'community', 'special'
    
    -- Requirements
    requirements JSONB, -- Criteria for earning the badge
    auto_award BOOLEAN DEFAULT FALSE, -- Automatically awarded or manually
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User badge awards
CREATE TABLE IF NOT EXISTS user_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES community_users(id),
    badge_id INTEGER REFERENCES community_badges(id),
    awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    awarded_by INTEGER REFERENCES community_users(id), -- NULL for auto-awards
    citation TEXT, -- Reason for manual awards
    
    UNIQUE(user_id, badge_id)
);

-- Community discussions and comments
CREATE TABLE IF NOT EXISTS community_discussions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,
    author_id INTEGER REFERENCES community_users(id),
    
    -- Discussion context
    context_type VARCHAR(50), -- 'funding_opportunity', 'general', 'feature_request'
    context_id INTEGER, -- ID of related item
    
    -- Engagement
    upvotes INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Moderation
    is_pinned BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Discussion replies
CREATE TABLE IF NOT EXISTS discussion_replies (
    id SERIAL PRIMARY KEY,
    discussion_id INTEGER REFERENCES community_discussions(id),
    parent_reply_id INTEGER REFERENCES discussion_replies(id), -- For threaded replies
    author_id INTEGER REFERENCES community_users(id),
    content TEXT NOT NULL,
    
    -- Engagement
    upvotes INTEGER DEFAULT 0,
    is_solution BOOLEAN DEFAULT FALSE, -- Mark as solution to question
    
    -- Moderation
    is_deleted BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regional community structure
CREATE TABLE IF NOT EXISTS regional_chapters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL, -- "West Africa", "East Africa", etc.
    description TEXT,
    countries TEXT[], -- Array of country codes
    
    -- Leadership
    ambassador_id INTEGER REFERENCES community_users(id),
    co_ambassadors INTEGER[], -- Additional regional leads
    
    -- Activity tracking
    member_count INTEGER DEFAULT 0,
    last_event TIMESTAMP,
    next_event TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event management
CREATE TABLE IF NOT EXISTS community_events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    type VARCHAR(50), -- 'call', 'workshop', 'bootcamp', 'conference'
    
    -- Scheduling
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Location/Access
    is_virtual BOOLEAN DEFAULT TRUE,
    meeting_url VARCHAR(500),
    recording_url VARCHAR(500),
    
    -- Organization
    organizer_id INTEGER REFERENCES community_users(id),
    regional_chapter_id INTEGER REFERENCES regional_chapters(id),
    max_participants INTEGER,
    
    -- Status
    registration_open BOOLEAN DEFAULT TRUE,
    is_published BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event registrations
CREATE TABLE IF NOT EXISTS event_registrations (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES community_events(id),
    user_id INTEGER REFERENCES community_users(id),
    
    -- Registration details
    attended BOOLEAN DEFAULT FALSE,
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    feedback_comments TEXT,
    
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(event_id, user_id)
);

-- Success stories and case studies
CREATE TABLE IF NOT EXISTS success_stories (
    id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES community_users(id),
    title VARCHAR(500) NOT NULL,
    summary TEXT NOT NULL,
    full_story TEXT NOT NULL,
    
    -- Success details
    funding_source VARCHAR(500), -- Organization that provided funding
    funding_amount DECIMAL(15,2),
    funding_currency VARCHAR(10),
    project_description TEXT,
    impact_achieved TEXT,
    
    -- Metadata
    story_type VARCHAR(50), -- 'research_grant', 'startup_funding', 'scholarship', etc.
    ai_domain VARCHAR(100), -- 'healthcare', 'agriculture', 'education', etc.
    country VARCHAR(100),
    
    -- Publishing
    is_published BOOLEAN DEFAULT FALSE,
    featured BOOLEAN DEFAULT FALSE,
    publication_date TIMESTAMP,
    
    -- Engagement
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =======================================================
-- INDEXES FOR PERFORMANCE
-- =======================================================

-- User and contribution indexes
CREATE INDEX IF NOT EXISTS idx_community_users_role ON community_users(role);
CREATE INDEX IF NOT EXISTS idx_community_users_country ON community_users(country);
CREATE INDEX IF NOT EXISTS idx_community_users_active ON community_users(is_active, last_active);

CREATE INDEX IF NOT EXISTS idx_contributions_type_status ON community_contributions(type, status);
CREATE INDEX IF NOT EXISTS idx_contributions_contributor ON community_contributions(contributor_id);
CREATE INDEX IF NOT EXISTS idx_contributions_reviewer ON community_contributions(reviewer_id);

CREATE INDEX IF NOT EXISTS idx_reviews_contribution ON contribution_reviews(contribution_id);
CREATE INDEX IF NOT EXISTS idx_reviews_reviewer ON contribution_reviews(reviewer_id);

-- Discussion and engagement indexes  
CREATE INDEX IF NOT EXISTS idx_discussions_context ON community_discussions(context_type, context_id);
CREATE INDEX IF NOT EXISTS idx_discussions_author ON community_discussions(author_id);
CREATE INDEX IF NOT EXISTS idx_discussions_activity ON community_discussions(last_activity DESC);

CREATE INDEX IF NOT EXISTS idx_replies_discussion ON discussion_replies(discussion_id);
CREATE INDEX IF NOT EXISTS idx_replies_parent ON discussion_replies(parent_reply_id);

-- Event and story indexes
CREATE INDEX IF NOT EXISTS idx_events_time ON community_events(start_time);
CREATE INDEX IF NOT EXISTS idx_events_chapter ON community_events(regional_chapter_id);

CREATE INDEX IF NOT EXISTS idx_stories_published ON success_stories(is_published, publication_date DESC);
CREATE INDEX IF NOT EXISTS idx_stories_country ON success_stories(country);
CREATE INDEX IF NOT EXISTS idx_stories_domain ON success_stories(ai_domain);

-- =======================================================
-- HELPER FUNCTIONS
-- =======================================================

-- Function to calculate user reputation score
CREATE OR REPLACE FUNCTION calculate_user_reputation(user_id INTEGER) RETURNS INTEGER AS $$
DECLARE
    reputation INTEGER := 0;
    contribution_points INTEGER;
    validation_points INTEGER;
    badge_points INTEGER;
BEGIN
    -- Points for approved contributions
    SELECT COALESCE(COUNT(*) * 10, 0) INTO contribution_points
    FROM community_contributions 
    WHERE contributor_id = user_id AND status = 'approved';
    
    -- Points for quality reviews
    SELECT COALESCE(COUNT(*) * 5, 0) INTO validation_points
    FROM contribution_reviews 
    WHERE reviewer_id = user_id;
    
    -- Points for badges (special badges worth more)
    SELECT COALESCE(COUNT(*) * 20, 0) INTO badge_points
    FROM user_badges ub
    JOIN community_badges cb ON ub.badge_id = cb.id
    WHERE ub.user_id = user_id;
    
    reputation := contribution_points + validation_points + badge_points;
    
    -- Update user record
    UPDATE community_users 
    SET reputation_score = reputation 
    WHERE id = user_id;
    
    RETURN reputation;
END;
$$ LANGUAGE plpgsql;

-- Function to check badge eligibility
CREATE OR REPLACE FUNCTION check_badge_eligibility(user_id INTEGER, badge_name VARCHAR(100)) RETURNS BOOLEAN AS $$
DECLARE
    badge_req JSONB;
    user_stats RECORD;
BEGIN
    -- Get badge requirements
    SELECT requirements INTO badge_req
    FROM community_badges
    WHERE name = badge_name;
    
    -- Get user statistics
    SELECT 
        contribution_count,
        validation_count,
        reputation_score
    INTO user_stats
    FROM community_users
    WHERE id = user_id;
    
    -- Check specific badge requirements (simplified example)
    IF badge_name = 'New Contributor' THEN
        RETURN user_stats.contribution_count >= 1;
    ELSIF badge_name = 'Opportunity Hunter' THEN
        RETURN user_stats.contribution_count >= 10;
    ELSIF badge_name = 'Quality Validator' THEN
        RETURN user_stats.validation_count >= 50;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- =======================================================
-- INITIAL DATA SETUP
-- =======================================================

-- Insert community badges
INSERT INTO community_badges (name, description, icon, category, requirements, auto_award) VALUES
('New Contributor', 'Welcome to the community! Your first approved contribution.', '🌱', 'contribution', '{"min_contributions": 1}', TRUE),
('Opportunity Hunter', 'Discovered and shared 10+ funding opportunities.', '🔍', 'contribution', '{"min_contributions": 10}', TRUE),
('Quality Validator', 'Provided 50+ helpful peer reviews.', '✅', 'validation', '{"min_validations": 50}', TRUE),
('Translation Expert', 'Improved 100+ translations for better accessibility.', '🌐', 'contribution', '{"min_translations": 100}', TRUE),
('Knowledge Sharer', 'Shared 5+ success stories or best practices.', '📚', 'community', '{"min_stories": 5}', TRUE),
('Regional Champion', 'Top contributor in their country/region.', '🎯', 'special', '{"type": "manual"}', FALSE),
('Platform Hero', 'Outstanding overall contribution to the platform.', '💎', 'special', '{"type": "manual"}', FALSE),
('Community Leader', 'Active in community governance and mentorship.', '👑', 'special', '{"type": "manual"}', FALSE)
ON CONFLICT (name) DO NOTHING;

-- Insert regional chapters
INSERT INTO regional_chapters (name, description, countries) VALUES
('West Africa', 'Community chapter for West African countries', ARRAY['NG', 'GH', 'SN', 'CI', 'BF', 'ML', 'SL', 'LR', 'GN', 'BJ', 'TG', 'GW', 'MR', 'NE']),
('East Africa', 'Community chapter for East African countries', ARRAY['KE', 'UG', 'TZ', 'RW', 'ET', 'SO', 'DJ', 'ER', 'SS']),
('Southern Africa', 'Community chapter for Southern African countries', ARRAY['ZA', 'ZW', 'BW', 'ZM', 'MW', 'MZ', 'SZ', 'LS', 'NA', 'AO']),
('North Africa', 'Community chapter for North African countries', ARRAY['EG', 'LY', 'TN', 'DZ', 'MA', 'SD']),
('Central Africa', 'Community chapter for Central African countries', ARRAY['CD', 'CG', 'CF', 'CM', 'TD', 'GQ', 'GA', 'ST'])
ON CONFLICT (name) DO NOTHING;

-- =======================================================
-- VIEWS FOR COMMUNITY ANALYTICS
-- =======================================================

-- Community leaderboard view
CREATE OR REPLACE VIEW community_leaderboard AS
SELECT 
    cu.id,
    cu.username,
    cu.full_name,
    cu.country,
    cu.contribution_count,
    cu.validation_count,
    cu.reputation_score,
    array_length(cu.badges, 1) as badge_count,
    cu.last_active,
    RANK() OVER (ORDER BY cu.reputation_score DESC) as reputation_rank
FROM community_users cu
WHERE cu.is_active = TRUE
ORDER BY cu.reputation_score DESC;

-- Recent community activity view
CREATE OR REPLACE VIEW recent_community_activity AS
SELECT 
    'contribution' as activity_type,
    cc.id as activity_id,
    cu.username,
    cc.type as activity_subtype,
    cc.created_at
FROM community_contributions cc
JOIN community_users cu ON cc.contributor_id = cu.id
WHERE cc.created_at > NOW() - INTERVAL '30 days'

UNION ALL

SELECT 
    'review' as activity_type,
    cr.id as activity_id,
    cu.username,
    cr.review_type as activity_subtype,
    cr.created_at
FROM contribution_reviews cr
JOIN community_users cu ON cr.reviewer_id = cu.id
WHERE cr.created_at > NOW() - INTERVAL '30 days'

UNION ALL

SELECT 
    'discussion' as activity_type,
    cd.id as activity_id,
    cu.username,
    cd.context_type as activity_subtype,
    cd.created_at
FROM community_discussions cd
JOIN community_users cu ON cd.author_id = cu.id
WHERE cd.created_at > NOW() - INTERVAL '30 days'

ORDER BY created_at DESC;

-- Community health metrics view
CREATE OR REPLACE VIEW community_health_metrics AS
SELECT 
    (SELECT COUNT(*) FROM community_users WHERE is_active = TRUE) as active_users,
    (SELECT COUNT(*) FROM community_contributions WHERE created_at > NOW() - INTERVAL '30 days') as monthly_contributions,
    (SELECT COUNT(*) FROM contribution_reviews WHERE created_at > NOW() - INTERVAL '30 days') as monthly_reviews,
    (SELECT AVG(rating) FROM contribution_reviews WHERE created_at > NOW() - INTERVAL '30 days') as avg_review_rating,
    (SELECT COUNT(DISTINCT country) FROM community_users WHERE is_active = TRUE) as countries_represented,
    (SELECT COUNT(*) FROM success_stories WHERE is_published = TRUE) as published_stories;

"""

# =======================================================
# SUCCESS MESSAGE
# =======================================================

def print_community_setup_message():
    print("""
    ✅ TAIFA-FIALA Community Infrastructure Schema Ready!
    
    📊 Tables Created:
    ├── community_users (user accounts and profiles)
    ├── community_contributions (submission tracking)
    ├── contribution_reviews (peer review system)
    ├── community_badges (achievement system)
    ├── user_badges (badge awards)
    ├── community_discussions (forum system)
    ├── discussion_replies (threaded discussions)
    ├── regional_chapters (geographic organization)
    ├── community_events (event management)
    ├── event_registrations (event attendance)
    └── success_stories (impact documentation)
    
    🔍 Views Created:
    ├── community_leaderboard (reputation rankings)
    ├── recent_community_activity (activity feed)
    └── community_health_metrics (engagement stats)
    
    ⚡ Functions Created:
    ├── calculate_user_reputation() (scoring system)
    └── check_badge_eligibility() (achievement logic)
    
    🎯 Ready for Community Features:
    ├── User registration and profiles
    ├── Content submission workflow
    ├── Peer review and validation
    ├── Badge and recognition system
    ├── Regional community organization
    ├── Event management
    ├── Success story documentation
    └── Community analytics and health monitoring
    """)

if __name__ == "__main__":
    print_community_setup_message()