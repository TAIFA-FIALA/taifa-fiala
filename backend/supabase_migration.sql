-- TAIFA-FIALA Database Schema
-- This file contains the complete schema for the TAIFA-FIALA platform
-- Execute this in the Supabase SQL Editor

-- Health check table for testing connectivity
CREATE TABLE IF NOT EXISTS health_check (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) DEFAULT 'OK',
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO health_check (status) VALUES ('OK');

-- Organizations table with role distinctions
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    website VARCHAR(255),
    logo_url VARCHAR(255),
    headquarters_country VARCHAR(100),
    headquarters_city VARCHAR(100),
    founded_year INTEGER,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    social_media_links JSONB,
    ai_domains JSONB,
    geographic_scopes JSONB,
    
    -- Organization role fields
    role VARCHAR(20) CHECK (role IN ('provider', 'recipient', 'both')),
    provider_type VARCHAR(50) CHECK (provider_type IN ('granting_agency', 'venture_capital', 'angel_investor', 'accelerator', NULL)),
    recipient_type VARCHAR(50) CHECK (recipient_type IN ('grantee', 'startup', 'research_institution', 'non_profit', NULL)),
    startup_stage VARCHAR(50) CHECK (startup_stage IN ('idea', 'prototype', 'seed', 'early_growth', 'expansion', NULL)),
    
    -- Equity and inclusion tracking
    women_led BOOLEAN DEFAULT FALSE,
    underrepresented_led BOOLEAN DEFAULT FALSE,
    inclusion_details JSONB,
    equity_score FLOAT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for organizations
CREATE INDEX IF NOT EXISTS idx_organizations_role ON organizations(role);
CREATE INDEX IF NOT EXISTS idx_organizations_provider_type ON organizations(provider_type);
CREATE INDEX IF NOT EXISTS idx_organizations_recipient_type ON organizations(recipient_type);
CREATE INDEX IF NOT EXISTS idx_organizations_women_led ON organizations(women_led);
CREATE INDEX IF NOT EXISTS idx_organizations_underrepresented_led ON organizations(underrepresented_led);

-- Funding types table with category distinctions
CREATE TABLE IF NOT EXISTS funding_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Enhanced funding category tracking
    category VARCHAR(50) CHECK (category IN ('grant', 'investment', 'prize', 'other')),
    requires_equity BOOLEAN DEFAULT FALSE,
    requires_repayment BOOLEAN DEFAULT FALSE,
    typical_duration_months INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_funding_types_category ON funding_types(category);

-- Funding opportunities table with specialized properties
CREATE TABLE IF NOT EXISTS funding_opportunities (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    amount_min NUMERIC,
    amount_max NUMERIC,
    application_deadline DATE,
    application_url VARCHAR(255),
    eligibility_criteria JSONB,
    ai_domains JSONB,
    geographic_scopes JSONB,
    funding_type_id INTEGER REFERENCES funding_types(id),
    
    -- Organization relationship fields with enhanced roles
    provider_organization_id INTEGER REFERENCES organizations(id),
    recipient_organization_id INTEGER REFERENCES organizations(id),
    
    -- Grant-specific properties
    grant_reporting_requirements TEXT,
    grant_duration_months INTEGER,
    grant_renewable BOOLEAN DEFAULT FALSE,
    
    -- Investment-specific properties
    equity_percentage FLOAT,
    valuation_cap NUMERIC,
    interest_rate FLOAT,
    expected_roi FLOAT,
    
    -- Additional fields
    status VARCHAR(50) DEFAULT 'active',
    additional_resources JSONB,
    equity_focus_details JSONB,
    women_focus BOOLEAN DEFAULT FALSE,
    underserved_focus BOOLEAN DEFAULT FALSE,
    youth_focus BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for funding opportunities
CREATE INDEX IF NOT EXISTS idx_funding_opportunities_provider_org ON funding_opportunities(provider_organization_id);
CREATE INDEX IF NOT EXISTS idx_funding_opportunities_recipient_org ON funding_opportunities(recipient_organization_id);
CREATE INDEX IF NOT EXISTS idx_funding_opportunities_funding_type ON funding_opportunities(funding_type_id);
CREATE INDEX IF NOT EXISTS idx_funding_opportunities_women_focus ON funding_opportunities(women_focus);
CREATE INDEX IF NOT EXISTS idx_funding_opportunities_underserved_focus ON funding_opportunities(underserved_focus);
CREATE INDEX IF NOT EXISTS idx_funding_opportunities_youth_focus ON funding_opportunities(youth_focus);
