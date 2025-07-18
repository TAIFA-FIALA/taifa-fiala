/*
Comprehensive CRM, Projects, and Financial Database Schema for AI in Africa
==========================================================================

This schema transforms the existing funding intelligence platform into a complete
business management system covering:

1. CUSTOMER RELATIONSHIP MANAGEMENT (CRM)
2. PROJECT MANAGEMENT & TRACKING
3. FINANCIAL MANAGEMENT & BUDGETING
4. DOCUMENT MANAGEMENT
5. COMMUNICATION TRACKING
6. WORKFLOW MANAGEMENT
7. BUSINESS INTELLIGENCE & ANALYTICS

Built for the African AI ecosystem - capturing organizations, people, projects,
investments, partnerships, and the complete funding lifecycle.

Target: 10M+ organizations, 100M+ individuals, 1M+ projects, 10M+ transactions
*/

-- ==========================================
-- 1. CUSTOMER RELATIONSHIP MANAGEMENT (CRM)
-- ==========================================

-- Enhanced People/Contacts Management
CREATE TABLE IF NOT EXISTS contacts (
    id BIGSERIAL PRIMARY KEY,
    
    -- Basic Information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(200) GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
    title VARCHAR(100),
    job_title VARCHAR(150),
    department VARCHAR(100),
    
    -- Contact Information
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    mobile VARCHAR(50),
    linkedin_url VARCHAR(500),
    twitter_handle VARCHAR(100),
    website VARCHAR(500),
    
    -- Address Information
    street_address TEXT,
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    
    -- Organization Relationship
    organization_id BIGINT REFERENCES organizations(id),
    is_primary_contact BOOLEAN DEFAULT FALSE,
    reporting_to_contact_id BIGINT REFERENCES contacts(id), -- Org chart
    
    -- Contact Classification
    contact_type VARCHAR(50) DEFAULT 'individual', -- 'individual', 'founder', 'executive', 'researcher', 'investor'
    contact_source VARCHAR(100), -- How we found them
    contact_quality_score DECIMAL(3,2) DEFAULT 0.0,
    
    -- AI Analysis
    ai_influence_score DECIMAL(3,2) DEFAULT 0.0, -- Influence in AI community
    expertise_areas TEXT[], -- Array of expertise areas
    languages_spoken TEXT[], -- Languages they speak
    
    -- Preferences
    communication_preferences JSONB, -- Email, phone, preferred times
    timezone VARCHAR(50),
    privacy_settings JSONB,
    
    -- Relationship Management
    relationship_status VARCHAR(50) DEFAULT 'prospect', -- 'prospect', 'active', 'partner', 'alumni', 'inactive'
    relationship_strength VARCHAR(20) DEFAULT 'cold', -- 'cold', 'warm', 'hot'
    last_contact_date TIMESTAMP,
    next_follow_up_date TIMESTAMP,
    
    -- Engagement Tracking
    email_opens INTEGER DEFAULT 0,
    email_clicks INTEGER DEFAULT 0,
    meeting_count INTEGER DEFAULT 0,
    last_engagement_date TIMESTAMP,
    engagement_score DECIMAL(5,2) DEFAULT 0.0,
    
    -- Status and Metadata
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'do_not_contact'
    tags TEXT[], -- Flexible tagging
    notes TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER,
    updated_by INTEGER,
    
    -- Constraints
    CONSTRAINT valid_contact_quality CHECK (contact_quality_score >= 0 AND contact_quality_score <= 1),
    CONSTRAINT valid_ai_influence CHECK (ai_influence_score >= 0 AND ai_influence_score <= 1),
    CONSTRAINT valid_engagement_score CHECK (engagement_score >= 0)
);

-- Contact Interactions (Communication History)
CREATE TABLE IF NOT EXISTS contact_interactions (
    id BIGSERIAL PRIMARY KEY,
    
    -- Core References
    contact_id BIGINT NOT NULL REFERENCES contacts(id),
    organization_id BIGINT REFERENCES organizations(id),
    project_id BIGINT REFERENCES projects(id), -- Will be defined below
    
    -- Interaction Details
    interaction_type VARCHAR(50) NOT NULL, -- 'email', 'call', 'meeting', 'social', 'event'
    interaction_method VARCHAR(50), -- 'inbound', 'outbound', 'automated'
    subject VARCHAR(500),
    description TEXT,
    
    -- Timing
    interaction_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER,
    
    -- Outcome
    outcome VARCHAR(100), -- 'positive', 'negative', 'neutral', 'follow_up_required'
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date TIMESTAMP,
    
    -- Engagement Metrics
    engagement_score DECIMAL(3,2) DEFAULT 0.0,
    conversion_score DECIMAL(3,2) DEFAULT 0.0,
    
    -- Metadata
    interaction_metadata JSONB,
    tags TEXT[],
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER,
    
    -- Constraints
    CONSTRAINT valid_engagement_score CHECK (engagement_score >= 0 AND engagement_score <= 1),
    CONSTRAINT valid_conversion_score CHECK (conversion_score >= 0 AND conversion_score <= 1)
);

-- Contact Networks (Relationship Mapping)
CREATE TABLE IF NOT EXISTS contact_networks (
    id BIGSERIAL PRIMARY KEY,
    
    -- Relationship
    contact_a_id BIGINT NOT NULL REFERENCES contacts(id),
    contact_b_id BIGINT NOT NULL REFERENCES contacts(id),
    
    -- Relationship Details
    relationship_type VARCHAR(50) NOT NULL, -- 'colleague', 'mentor', 'advisor', 'collaborator', 'competitor'
    relationship_strength VARCHAR(20) DEFAULT 'weak', -- 'weak', 'moderate', 'strong'
    relationship_direction VARCHAR(20) DEFAULT 'bidirectional', -- 'bidirectional', 'a_to_b', 'b_to_a'
    
    -- Context
    context VARCHAR(200), -- How they know each other
    organization_context VARCHAR(200), -- Organizational context
    project_context VARCHAR(200), -- Project context
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT no_self_relationship CHECK (contact_a_id != contact_b_id),
    CONSTRAINT unique_relationship UNIQUE (contact_a_id, contact_b_id)
);

-- ==========================================
-- 2. PROJECT MANAGEMENT & TRACKING
-- ==========================================

-- Projects (Complete Lifecycle Management)
CREATE TABLE IF NOT EXISTS projects (
    id BIGSERIAL PRIMARY KEY,
    
    -- Basic Information
    name VARCHAR(200) NOT NULL,
    description TEXT,
    project_code VARCHAR(50) UNIQUE, -- Internal project code
    
    -- Project Classification
    project_type VARCHAR(50) NOT NULL, -- 'funding_application', 'research', 'product_development', 'partnership'
    project_category VARCHAR(100), -- 'AI_healthcare', 'AI_education', 'AI_agriculture', etc.
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    
    -- Relationships
    organization_id BIGINT REFERENCES organizations(id),
    funding_opportunity_id BIGINT REFERENCES funding_opportunities(id),
    parent_project_id BIGINT REFERENCES projects(id), -- For sub-projects
    
    -- Project Management
    project_manager_id BIGINT REFERENCES contacts(id),
    project_sponsor_id BIGINT REFERENCES contacts(id),
    project_team_lead_id BIGINT REFERENCES contacts(id),
    
    -- Timeline
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    
    -- Status and Progress
    status VARCHAR(50) DEFAULT 'planning', -- 'planning', 'active', 'on_hold', 'completed', 'cancelled'
    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
    health_status VARCHAR(20) DEFAULT 'green', -- 'green', 'yellow', 'red'
    
    -- Financial
    total_budget DECIMAL(15,2),
    currency VARCHAR(10) DEFAULT 'USD',
    spent_amount DECIMAL(15,2) DEFAULT 0.0,
    remaining_budget DECIMAL(15,2) GENERATED ALWAYS AS (total_budget - spent_amount) STORED,
    
    -- Funding Information
    funding_stage VARCHAR(50), -- 'pre_seed', 'seed', 'series_a', 'series_b', 'growth', 'ipo'
    funding_amount_requested DECIMAL(15,2),
    funding_amount_received DECIMAL(15,2),
    funding_status VARCHAR(50) DEFAULT 'planning', -- 'planning', 'applied', 'under_review', 'approved', 'rejected'
    
    -- AI/Tech Focus
    ai_technologies TEXT[], -- Array of AI technologies used
    application_domains TEXT[], -- Array of application domains
    target_market VARCHAR(200),
    geographic_focus TEXT[], -- Array of geographic regions
    
    -- Impact Metrics
    expected_impact_metrics JSONB,
    actual_impact_metrics JSONB,
    success_metrics JSONB,
    
    -- Risk Management
    risk_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high'
    risk_factors TEXT[],
    mitigation_strategies TEXT[],
    
    -- Communication
    communication_frequency VARCHAR(50) DEFAULT 'weekly', -- 'daily', 'weekly', 'bi_weekly', 'monthly'
    last_status_update TIMESTAMP,
    next_milestone_date DATE,
    
    -- Metadata
    tags TEXT[],
    external_references JSONB, -- Links to external systems
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER,
    updated_by INTEGER,
    
    -- Constraints
    CONSTRAINT valid_progress CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    CONSTRAINT valid_budget CHECK (total_budget >= 0),
    CONSTRAINT valid_spent CHECK (spent_amount >= 0),
    CONSTRAINT valid_dates CHECK (planned_start_date <= planned_end_date)
);

-- Project Milestones
CREATE TABLE IF NOT EXISTS project_milestones (
    id BIGSERIAL PRIMARY KEY,
    
    -- Core References
    project_id BIGINT NOT NULL REFERENCES projects(id),
    
    -- Milestone Details
    name VARCHAR(200) NOT NULL,
    description TEXT,
    milestone_type VARCHAR(50) DEFAULT 'deliverable', -- 'deliverable', 'checkpoint', 'review', 'funding'
    
    -- Timeline
    planned_date DATE NOT NULL,
    actual_date DATE,
    
    -- Status
    status VARCHAR(50) DEFAULT 'planned', -- 'planned', 'in_progress', 'completed', 'delayed', 'cancelled'
    completion_percentage DECIMAL(5,2) DEFAULT 0.0,
    
    -- Dependencies
    depends_on_milestone_id BIGINT REFERENCES project_milestones(id),
    blocking_milestones BOOLEAN DEFAULT FALSE,
    
    -- Deliverables
    deliverable_description TEXT,
    deliverable_format VARCHAR(100), -- 'document', 'software', 'presentation', 'prototype'
    deliverable_location VARCHAR(500), -- Where deliverable is stored
    
    -- Quality Assurance
    quality_criteria TEXT,
    acceptance_criteria TEXT,
    review_required BOOLEAN DEFAULT FALSE,
    reviewer_id BIGINT REFERENCES contacts(id),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_completion CHECK (completion_percentage >= 0 AND completion_percentage <= 100)
);

-- Project Team Members
CREATE TABLE IF NOT EXISTS project_team_members (
    id BIGSERIAL PRIMARY KEY,
    
    -- Core References
    project_id BIGINT NOT NULL REFERENCES projects(id),
    contact_id BIGINT NOT NULL REFERENCES contacts(id),
    
    -- Role Information
    role VARCHAR(100) NOT NULL, -- 'project_manager', 'developer', 'researcher', 'advisor', 'stakeholder'
    responsibilities TEXT,
    
    -- Engagement
    start_date DATE,
    end_date DATE,
    allocation_percentage DECIMAL(5,2) DEFAULT 100.0, -- % of time allocated
    
    -- Permissions
    access_level VARCHAR(50) DEFAULT 'member', -- 'viewer', 'member', 'admin', 'owner'
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'on_leave'
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_allocation CHECK (allocation_percentage >= 0 AND allocation_percentage <= 100),
    CONSTRAINT unique_project_contact UNIQUE (project_id, contact_id)
);

-- Project Communications
CREATE TABLE IF NOT EXISTS project_communications (
    id BIGSERIAL PRIMARY KEY,
    
    -- Core References
    project_id BIGINT NOT NULL REFERENCES projects(id),
    sender_id BIGINT REFERENCES contacts(id),
    
    -- Communication Details
    communication_type VARCHAR(50) NOT NULL, -- 'status_update', 'meeting_notes', 'decision', 'issue', 'announcement'
    subject VARCHAR(500),
    message TEXT,
    
    -- Recipients
    recipients JSONB, -- Array of contact IDs and external emails
    
    -- Metadata
    communication_date TIMESTAMP DEFAULT NOW(),
    priority VARCHAR(20) DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    
    -- Status
    status VARCHAR(20) DEFAULT 'sent', -- 'draft', 'sent', 'read', 'acknowledged'
    
    -- Attachments
    attachments JSONB, -- Array of attachment information
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 3. FINANCIAL MANAGEMENT & BUDGETING
-- ==========================================

-- Budget Categories
CREATE TABLE IF NOT EXISTS budget_categories (
    id SERIAL PRIMARY KEY,
    
    -- Category Information
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category_code VARCHAR(20) UNIQUE,
    
    -- Hierarchy
    parent_category_id INTEGER REFERENCES budget_categories(id),
    category_level INTEGER DEFAULT 0,
    category_path TEXT, -- For hierarchical queries
    
    -- Classification
    category_type VARCHAR(50) DEFAULT 'expense', -- 'expense', 'revenue', 'capital'
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Budgets
CREATE TABLE IF NOT EXISTS budgets (
    id BIGSERIAL PRIMARY KEY,
    
    -- Basic Information
    name VARCHAR(200) NOT NULL,
    description TEXT,
    budget_code VARCHAR(50) UNIQUE,
    
    -- Relationships
    organization_id BIGINT REFERENCES organizations(id),
    project_id BIGINT REFERENCES projects(id),
    owner_id BIGINT REFERENCES contacts(id),
    
    -- Budget Period
    budget_period_type VARCHAR(50) DEFAULT 'annual', -- 'monthly', 'quarterly', 'annual', 'project'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Financial Details
    total_budget DECIMAL(15,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'approved', 'active', 'closed'
    approval_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    approved_by_id BIGINT REFERENCES contacts(id),
    approved_at TIMESTAMP,
    
    -- Tracking
    spent_amount DECIMAL(15,2) DEFAULT 0.0,
    committed_amount DECIMAL(15,2) DEFAULT 0.0,
    remaining_amount DECIMAL(15,2) GENERATED ALWAYS AS (total_budget - spent_amount - committed_amount) STORED,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER,
    updated_by INTEGER,
    
    -- Constraints
    CONSTRAINT valid_budget CHECK (total_budget >= 0),
    CONSTRAINT valid_spent CHECK (spent_amount >= 0),
    CONSTRAINT valid_committed CHECK (committed_amount >= 0),
    CONSTRAINT valid_dates CHECK (start_date <= end_date)
);

-- Budget Line Items
CREATE TABLE IF NOT EXISTS budget_line_items (
    id BIGSERIAL PRIMARY KEY,
    
    -- Core References
    budget_id BIGINT NOT NULL REFERENCES budgets(id),
    budget_category_id INTEGER REFERENCES budget_categories(id),
    
    -- Line Item Details
    name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Financial Details
    budgeted_amount DECIMAL(15,2) NOT NULL,
    spent_amount DECIMAL(15,2) DEFAULT 0.0,
    committed_amount DECIMAL(15,2) DEFAULT 0.0,
    remaining_amount DECIMAL(15,2) GENERATED ALWAYS AS (budgeted_amount - spent_amount - committed_amount) STORED,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_budgeted CHECK (budgeted_amount >= 0),
    CONSTRAINT valid_line_spent CHECK (spent_amount >= 0),
    CONSTRAINT valid_line_committed CHECK (committed_amount >= 0)
);

-- Financial Transactions
CREATE TABLE IF NOT EXISTS financial_transactions (
    id BIGSERIAL PRIMARY KEY,
    
    -- Core References
    organization_id BIGINT REFERENCES organizations(id),
    project_id BIGINT REFERENCES projects(id),
    budget_id BIGINT REFERENCES budgets(id),
    budget_line_item_id BIGINT REFERENCES budget_line_items(id),
    
    -- Transaction Details
    transaction_type VARCHAR(50) NOT NULL, -- 'revenue', 'expense', 'transfer', 'adjustment'
    transaction_category VARCHAR(100),
    description TEXT,
    
    -- Financial Details
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    
    -- Parties
    from_party VARCHAR(200), -- Who/what the money comes from
    to_party VARCHAR(200), -- Who/what the money goes to
    
    -- Timing
    transaction_date DATE NOT NULL,
    due_date DATE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'completed', 'cancelled'
    
    -- References
    invoice_number VARCHAR(100),
    purchase_order_number VARCHAR(100),
    reference_number VARCHAR(100),
    
    -- Approval
    approved_by_id BIGINT REFERENCES contacts(id),
    approved_at TIMESTAMP,
    
    -- Metadata
    tags TEXT[],
    notes TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER,
    
    -- Constraints
    CONSTRAINT valid_amount CHECK (amount != 0) -- Can be positive or negative
);

-- ==========================================
-- 4. DOCUMENT MANAGEMENT
-- ==========================================

-- Document Categories
CREATE TABLE IF NOT EXISTS document_categories (
    id SERIAL PRIMARY KEY,
    
    -- Category Information
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Hierarchy
    parent_category_id INTEGER REFERENCES document_categories(id),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    
    -- Core References
    organization_id BIGINT REFERENCES organizations(id),
    project_id BIGINT REFERENCES projects(id),
    contact_id BIGINT REFERENCES contacts(id),
    
    -- Document Information
    name VARCHAR(200) NOT NULL,
    description TEXT,
    document_type VARCHAR(50) NOT NULL, -- 'contract', 'proposal', 'report', 'presentation', 'legal'
    document_category_id INTEGER REFERENCES document_categories(id),
    
    -- File Information
    file_name VARCHAR(255),
    file_path VARCHAR(1000),
    file_size BIGINT,
    file_type VARCHAR(50),
    file_hash VARCHAR(64), -- For integrity checking
    
    -- Storage Information
    storage_type VARCHAR(50) DEFAULT 'local', -- 'local', 's3', 'google_cloud', 'azure'
    storage_location VARCHAR(1000),
    
    -- Version Control
    version_number VARCHAR(20) DEFAULT '1.0',
    is_current_version BOOLEAN DEFAULT TRUE,
    parent_document_id BIGINT REFERENCES documents(id),
    
    -- Access Control
    access_level VARCHAR(50) DEFAULT 'private', -- 'public', 'organization', 'project', 'private'
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- 'draft', 'active', 'archived', 'deleted'
    
    -- Metadata
    tags TEXT[],
    created_by_id BIGINT REFERENCES contacts(id),
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_file_size CHECK (file_size >= 0)
);

-- Document Permissions
CREATE TABLE IF NOT EXISTS document_permissions (
    id BIGSERIAL PRIMARY KEY,
    
    -- Core References
    document_id BIGINT NOT NULL REFERENCES documents(id),
    contact_id BIGINT REFERENCES contacts(id),
    organization_id BIGINT REFERENCES organizations(id),
    
    -- Permission Details
    permission_type VARCHAR(50) NOT NULL, -- 'view', 'edit', 'delete', 'share'
    granted_by_id BIGINT REFERENCES contacts(id),
    
    -- Timing
    granted_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CONSTRAINT permission_subject_required CHECK (contact_id IS NOT NULL OR organization_id IS NOT NULL)
);

-- ==========================================
-- 5. COMMUNICATION MANAGEMENT
-- ==========================================

-- Email Templates
CREATE TABLE IF NOT EXISTS email_templates (
    id BIGSERIAL PRIMARY KEY,
    
    -- Template Information
    name VARCHAR(200) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL, -- 'welcome', 'follow_up', 'proposal', 'status_update'
    
    -- Content
    subject VARCHAR(500),
    body_html TEXT,
    body_text TEXT,
    
    -- Variables
    template_variables JSONB, -- Available variables for substitution
    
    -- Usage
    usage_count INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER
);

-- Email Campaigns
CREATE TABLE IF NOT EXISTS email_campaigns (
    id BIGSERIAL PRIMARY KEY,
    
    -- Campaign Information
    name VARCHAR(200) NOT NULL,
    description TEXT,
    campaign_type VARCHAR(50) DEFAULT 'general', -- 'general', 'funding_announcement', 'project_update'
    
    -- Template
    email_template_id BIGINT REFERENCES email_templates(id),
    
    -- Targeting
    target_audience JSONB, -- Criteria for targeting
    recipient_count INTEGER DEFAULT 0,
    
    -- Scheduling
    send_date TIMESTAMP,
    send_immediately BOOLEAN DEFAULT FALSE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'scheduled', 'sending', 'sent', 'cancelled'
    
    -- Metrics
    emails_sent INTEGER DEFAULT 0,
    emails_delivered INTEGER DEFAULT 0,
    emails_opened INTEGER DEFAULT 0,
    emails_clicked INTEGER DEFAULT 0,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER
);

-- Communication Logs (All Communications)
CREATE TABLE IF NOT EXISTS communication_logs (
    id BIGSERIAL PRIMARY KEY,
    
    -- Core References
    contact_id BIGINT REFERENCES contacts(id),
    organization_id BIGINT REFERENCES organizations(id),
    project_id BIGINT REFERENCES projects(id),
    
    -- Communication Details
    communication_type VARCHAR(50) NOT NULL, -- 'email', 'phone', 'meeting', 'social_media', 'letter'
    direction VARCHAR(20) NOT NULL, -- 'inbound', 'outbound'
    
    -- Content
    subject VARCHAR(500),
    message TEXT,
    
    -- Metadata
    communication_date TIMESTAMP DEFAULT NOW(),
    duration_minutes INTEGER,
    
    -- Status
    status VARCHAR(20) DEFAULT 'completed', -- 'scheduled', 'completed', 'failed', 'cancelled'
    
    -- Tracking
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    replied_at TIMESTAMP,
    
    -- Campaign Reference
    email_campaign_id BIGINT REFERENCES email_campaigns(id),
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT NOW(),
    logged_by INTEGER
);

-- ==========================================
-- 6. WORKFLOW MANAGEMENT
-- ==========================================

-- Workflow Definitions
CREATE TABLE IF NOT EXISTS workflow_definitions (
    id BIGSERIAL PRIMARY KEY,
    
    -- Workflow Information
    name VARCHAR(200) NOT NULL,
    description TEXT,
    workflow_type VARCHAR(50) NOT NULL, -- 'funding_application', 'project_approval', 'document_review'
    
    -- Configuration
    workflow_config JSONB, -- Workflow steps and configuration
    
    -- Triggers
    trigger_events TEXT[], -- Events that trigger this workflow
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    version_number VARCHAR(20) DEFAULT '1.0',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER
);

-- Workflow Instances
CREATE TABLE IF NOT EXISTS workflow_instances (
    id BIGSERIAL PRIMARY KEY,
    
    -- Core References
    workflow_definition_id BIGINT NOT NULL REFERENCES workflow_definitions(id),
    organization_id BIGINT REFERENCES organizations(id),
    project_id BIGINT REFERENCES projects(id),
    
    -- Instance Information
    instance_name VARCHAR(200),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'cancelled', 'failed'
    current_step VARCHAR(100),
    
    -- Progress
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    -- Data
    workflow_data JSONB, -- Data passed through workflow steps
    
    -- Audit Fields
    created_by INTEGER,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 7. BUSINESS INTELLIGENCE & ANALYTICS
-- ==========================================

-- Custom Reports
CREATE TABLE IF NOT EXISTS custom_reports (
    id BIGSERIAL PRIMARY KEY,
    
    -- Report Information
    name VARCHAR(200) NOT NULL,
    description TEXT,
    report_type VARCHAR(50) NOT NULL, -- 'financial', 'project', 'contact', 'custom'
    
    -- Configuration
    report_config JSONB, -- Query and display configuration
    
    -- Scheduling
    schedule_type VARCHAR(50) DEFAULT 'manual', -- 'manual', 'daily', 'weekly', 'monthly'
    schedule_config JSONB,
    
    -- Access
    owner_id BIGINT REFERENCES contacts(id),
    is_public BOOLEAN DEFAULT FALSE,
    
    -- Usage
    run_count INTEGER DEFAULT 0,
    last_run_at TIMESTAMP,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER
);

-- Analytics Events
CREATE TABLE IF NOT EXISTS analytics_events (
    id BIGSERIAL PRIMARY KEY,
    
    -- Event Information
    event_type VARCHAR(100) NOT NULL, -- 'page_view', 'document_download', 'email_open', 'funding_applied'
    event_category VARCHAR(50),
    event_action VARCHAR(100),
    
    -- Context
    user_id BIGINT REFERENCES contacts(id),
    organization_id BIGINT REFERENCES organizations(id),
    project_id BIGINT REFERENCES projects(id),
    
    -- Event Data
    event_data JSONB,
    
    -- Metadata
    event_timestamp TIMESTAMP DEFAULT NOW(),
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    
    -- Processing
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP
);

-- ==========================================
-- 8. INDEXES FOR PERFORMANCE
-- ==========================================

-- Contacts indexes
CREATE INDEX IF NOT EXISTS idx_contacts_organization_id ON contacts(organization_id);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_full_name ON contacts(full_name);
CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);
CREATE INDEX IF NOT EXISTS idx_contacts_contact_type ON contacts(contact_type);
CREATE INDEX IF NOT EXISTS idx_contacts_last_contact_date ON contacts(last_contact_date);
CREATE INDEX IF NOT EXISTS idx_contacts_relationship_status ON contacts(relationship_status);

-- Contact interactions indexes
CREATE INDEX IF NOT EXISTS idx_contact_interactions_contact_id ON contact_interactions(contact_id);
CREATE INDEX IF NOT EXISTS idx_contact_interactions_date ON contact_interactions(interaction_date);
CREATE INDEX IF NOT EXISTS idx_contact_interactions_type ON contact_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_contact_interactions_org_id ON contact_interactions(organization_id);

-- Projects indexes
CREATE INDEX IF NOT EXISTS idx_projects_organization_id ON projects(organization_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_project_manager_id ON projects(project_manager_id);
CREATE INDEX IF NOT EXISTS idx_projects_funding_opportunity_id ON projects(funding_opportunity_id);
CREATE INDEX IF NOT EXISTS idx_projects_start_date ON projects(planned_start_date);
CREATE INDEX IF NOT EXISTS idx_projects_end_date ON projects(planned_end_date);

-- Financial indexes
CREATE INDEX IF NOT EXISTS idx_budgets_organization_id ON budgets(organization_id);
CREATE INDEX IF NOT EXISTS idx_budgets_project_id ON budgets(project_id);
CREATE INDEX IF NOT EXISTS idx_budgets_status ON budgets(status);
CREATE INDEX IF NOT EXISTS idx_financial_transactions_org_id ON financial_transactions(organization_id);
CREATE INDEX IF NOT EXISTS idx_financial_transactions_project_id ON financial_transactions(project_id);
CREATE INDEX IF NOT EXISTS idx_financial_transactions_date ON financial_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_financial_transactions_type ON financial_transactions(transaction_type);

-- Documents indexes
CREATE INDEX IF NOT EXISTS idx_documents_organization_id ON documents(organization_id);
CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents(project_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);

-- Communication indexes
CREATE INDEX IF NOT EXISTS idx_communication_logs_contact_id ON communication_logs(contact_id);
CREATE INDEX IF NOT EXISTS idx_communication_logs_date ON communication_logs(communication_date);
CREATE INDEX IF NOT EXISTS idx_communication_logs_type ON communication_logs(communication_type);

-- Analytics indexes
CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON analytics_events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id);

-- ==========================================
-- 9. TRIGGERS FOR AUTOMATION
-- ==========================================

-- Update timestamps trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply timestamp triggers
CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_budgets_updated_at BEFORE UPDATE ON budgets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_budget_line_items_updated_at BEFORE UPDATE ON budget_line_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- 10. VIEWS FOR COMMON QUERIES
-- ==========================================

-- Contact Summary View
CREATE VIEW contact_summary AS
SELECT 
    c.id,
    c.full_name,
    c.email,
    c.job_title,
    o.name as organization_name,
    c.contact_type,
    c.relationship_status,
    c.last_contact_date,
    c.engagement_score,
    COUNT(ci.id) as interaction_count,
    MAX(ci.interaction_date) as last_interaction_date
FROM contacts c
LEFT JOIN organizations o ON c.organization_id = o.id
LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
GROUP BY c.id, c.full_name, c.email, c.job_title, o.name, c.contact_type, c.relationship_status, c.last_contact_date, c.engagement_score;

-- Project Dashboard View
CREATE VIEW project_dashboard AS
SELECT 
    p.id,
    p.name,
    p.project_type,
    p.status,
    p.progress_percentage,
    p.health_status,
    p.total_budget,
    p.spent_amount,
    p.remaining_budget,
    o.name as organization_name,
    pm.full_name as project_manager_name,
    p.planned_start_date,
    p.planned_end_date,
    COUNT(ptm.id) as team_member_count,
    COUNT(CASE WHEN pm_milestone.status = 'completed' THEN 1 END) as completed_milestones,
    COUNT(pm_milestone.id) as total_milestones
FROM projects p
LEFT JOIN organizations o ON p.organization_id = o.id
LEFT JOIN contacts pm ON p.project_manager_id = pm.id
LEFT JOIN project_team_members ptm ON p.id = ptm.project_id
LEFT JOIN project_milestones pm_milestone ON p.id = pm_milestone.project_id
GROUP BY p.id, p.name, p.project_type, p.status, p.progress_percentage, p.health_status, 
         p.total_budget, p.spent_amount, p.remaining_budget, o.name, pm.full_name, 
         p.planned_start_date, p.planned_end_date;

-- Financial Summary View
CREATE VIEW financial_summary AS
SELECT 
    o.id as organization_id,
    o.name as organization_name,
    COUNT(DISTINCT p.id) as project_count,
    SUM(p.total_budget) as total_project_budget,
    SUM(p.spent_amount) as total_spent,
    SUM(p.remaining_budget) as total_remaining,
    COUNT(DISTINCT ft.id) as transaction_count,
    SUM(CASE WHEN ft.transaction_type = 'revenue' THEN ft.amount ELSE 0 END) as total_revenue,
    SUM(CASE WHEN ft.transaction_type = 'expense' THEN ft.amount ELSE 0 END) as total_expenses
FROM organizations o
LEFT JOIN projects p ON o.id = p.organization_id
LEFT JOIN financial_transactions ft ON o.id = ft.organization_id
GROUP BY o.id, o.name;

-- ==========================================
-- 11. SAMPLE DATA FOR TESTING
-- ==========================================

-- Sample budget categories
INSERT INTO budget_categories (name, description, category_code, category_type) VALUES
('Personnel', 'Staff salaries and benefits', 'PERS', 'expense'),
('Equipment', 'Technology and equipment purchases', 'EQUIP', 'expense'),
('Travel', 'Travel and accommodation expenses', 'TRAVEL', 'expense'),
('Research', 'Research and development costs', 'R&D', 'expense'),
('Marketing', 'Marketing and promotion expenses', 'MARKET', 'expense'),
('Operations', 'General operational expenses', 'OPS', 'expense'),
('Grants', 'Grant funding received', 'GRANTS', 'revenue'),
('Investments', 'Investment funding received', 'INVEST', 'revenue')
ON CONFLICT (category_code) DO NOTHING;

-- Sample document categories
INSERT INTO document_categories (name, description) VALUES
('Legal Documents', 'Contracts, agreements, and legal documents'),
('Project Documents', 'Project proposals, reports, and deliverables'),
('Financial Documents', 'Budgets, invoices, and financial reports'),
('Technical Documents', 'Technical specifications and documentation'),
('Marketing Materials', 'Brochures, presentations, and marketing content')
ON CONFLICT DO NOTHING;

-- Sample email templates
INSERT INTO email_templates (name, description, template_type, subject, body_html, body_text) VALUES
('Welcome Email', 'Welcome new contacts to the platform', 'welcome', 
 'Welcome to AI Africa Funding Tracker', 
 '<p>Dear {{contact_name}},</p><p>Welcome to our platform!</p>',
 'Dear {{contact_name}}, Welcome to our platform!'),
('Follow Up Email', 'Follow up after initial contact', 'follow_up',
 'Following up on our conversation',
 '<p>Dear {{contact_name}},</p><p>Following up on our recent conversation...</p>',
 'Dear {{contact_name}}, Following up on our recent conversation...'),
('Project Update', 'Project status update email', 'status_update',
 'Project Update: {{project_name}}',
 '<p>Dear {{contact_name}},</p><p>Here is an update on {{project_name}}...</p>',
 'Dear {{contact_name}}, Here is an update on {{project_name}}...')
ON CONFLICT DO NOTHING;

-- ==========================================
-- 12. COMMENTS AND DOCUMENTATION
-- ==========================================

-- Table comments
COMMENT ON TABLE contacts IS 'Comprehensive contact management with CRM capabilities';
COMMENT ON TABLE contact_interactions IS 'All interactions with contacts - emails, calls, meetings';
COMMENT ON TABLE projects IS 'Complete project lifecycle management';
COMMENT ON TABLE budgets IS 'Budget planning and tracking';
COMMENT ON TABLE financial_transactions IS 'All financial transactions';
COMMENT ON TABLE documents IS 'Document management with version control';
COMMENT ON TABLE workflow_instances IS 'Workflow automation and tracking';

-- Column comments
COMMENT ON COLUMN contacts.ai_influence_score IS 'Influence score in AI community (0-1)';
COMMENT ON COLUMN contacts.engagement_score IS 'Overall engagement score based on interactions';
COMMENT ON COLUMN projects.health_status IS 'Project health: green (good), yellow (at risk), red (critical)';
COMMENT ON COLUMN budgets.remaining_amount IS 'Automatically calculated remaining budget';
COMMENT ON COLUMN financial_transactions.amount IS 'Transaction amount - positive for revenue, negative for expenses';

-- Performance hints
COMMENT ON INDEX idx_contacts_full_name IS 'Primary index for contact name searches';
COMMENT ON INDEX idx_projects_status IS 'Critical for project dashboard queries';
COMMENT ON INDEX idx_financial_transactions_date IS 'Essential for financial reporting queries';

-- Usage guidelines
COMMENT ON VIEW contact_summary IS 'Use this view for contact listings and CRM dashboards';
COMMENT ON VIEW project_dashboard IS 'Use this view for project management dashboards';
COMMENT ON VIEW financial_summary IS 'Use this view for financial reporting and analysis';

-- Schema completion notice
-- This schema provides a comprehensive foundation for:
-- 1. Customer Relationship Management (CRM)
-- 2. Project Management & Tracking
-- 3. Financial Management & Budgeting
-- 4. Document Management
-- 5. Communication Tracking
-- 6. Workflow Automation
-- 7. Business Intelligence & Analytics
-- 
-- The schema is designed to scale to millions of records and provides
-- the foundation for a complete business management system for the
-- African AI ecosystem.