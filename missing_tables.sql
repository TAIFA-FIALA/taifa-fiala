-- Missing Tables SQL Script for TAIFA-FIALA Database
-- Execute this in Supabase SQL Editor to create the missing tables

-- Geographic scopes reference table
CREATE TABLE IF NOT EXISTS geographic_scopes (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    code VARCHAR(10),
    region TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI domains reference table
CREATE TABLE IF NOT EXISTS ai_domains (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES ai_domains(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Community users table
CREATE TABLE IF NOT EXISTS community_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    funding_opportunity_id INTEGER REFERENCES funding_opportunities(id) ON DELETE CASCADE,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'submitted',
    amount_requested DECIMAL(15,2),
    amount_awarded DECIMAL(15,2),
    application_date DATE,
    decision_date DATE,
    submitted_by VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Funding rounds table
CREATE TABLE IF NOT EXISTS funding_rounds (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    round_name VARCHAR(100),
    round_type VARCHAR(50),
    amount_raised DECIMAL(15,2),
    valuation_pre DECIMAL(15,2),
    valuation_post DECIMAL(15,2),
    funding_date DATE,
    lead_investor VARCHAR(255),
    investors TEXT[],
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Investments table
CREATE TABLE IF NOT EXISTS investments (
    id SERIAL PRIMARY KEY,
    investor_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    recipient_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    funding_round_id INTEGER REFERENCES funding_rounds(id) ON DELETE SET NULL,
    amount DECIMAL(15,2),
    investment_type VARCHAR(50),
    equity_percentage DECIMAL(5,2),
    investment_date DATE,
    exit_date DATE,
    exit_amount DECIMAL(15,2),
    roi DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    metric_name VARCHAR(100),
    metric_value DECIMAL(15,2),
    metric_unit VARCHAR(20),
    measurement_date DATE,
    quarter INTEGER,
    year INTEGER,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Impact metrics table
CREATE TABLE IF NOT EXISTS impact_metrics (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    metric_name VARCHAR(100),
    metric_value DECIMAL(15,2),
    metric_unit VARCHAR(20),
    measurement_date DATE,
    beneficiaries_reached INTEGER,
    geographic_scope VARCHAR(100),
    sdg_alignment VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Partnerships table
CREATE TABLE IF NOT EXISTS partnerships (
    id SERIAL PRIMARY KEY,
    organization_a_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    organization_b_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    partnership_type VARCHAR(50),
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Research projects table
CREATE TABLE IF NOT EXISTS research_projects (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(500),
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    funding_amount DECIMAL(15,2),
    principal_investigator VARCHAR(255),
    collaborators TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Publications table
CREATE TABLE IF NOT EXISTS publications (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    research_project_id INTEGER REFERENCES research_projects(id) ON DELETE SET NULL,
    title VARCHAR(500),
    authors TEXT[],
    publication_date DATE,
    journal VARCHAR(255),
    doi VARCHAR(255),
    url VARCHAR(500),
    citation_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(500),
    description TEXT,
    event_date DATE,
    location VARCHAR(255),
    event_type VARCHAR(50),
    capacity INTEGER,
    registration_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Announcements table
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(500),
    content TEXT,
    announcement_type VARCHAR(50),
    published_date DATE,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Discussions table
CREATE TABLE IF NOT EXISTS discussions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES community_users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    content TEXT,
    category VARCHAR(50),
    is_pinned BOOLEAN DEFAULT FALSE,
    reply_count INTEGER DEFAULT 0,
    last_reply_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Resources table
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(500),
    description TEXT,
    resource_type VARCHAR(50),
    url VARCHAR(500),
    file_path VARCHAR(500),
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES community_users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    bio TEXT,
    location VARCHAR(255),
    organization_id INTEGER REFERENCES organizations(id) ON DELETE SET NULL,
    expertise_areas TEXT[],
    linkedin_url VARCHAR(500),
    twitter_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES community_users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    message TEXT,
    type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    related_id INTEGER,
    related_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add health check data
INSERT INTO health_check (status) VALUES ('OK') ON CONFLICT DO NOTHING;

-- Success message
SELECT 'Missing tables created successfully!' as message;