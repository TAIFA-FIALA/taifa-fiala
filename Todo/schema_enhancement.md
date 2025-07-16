# TAIFA-FIALA Database Schema Enhancement Plan

## Priority 1: Address Geographic Equity (Immediate Implementation)

### 1.1 Enhanced Geographic Tracking
```sql
-- Add to organizations table
ALTER TABLE organizations ADD COLUMN headquarters_country VARCHAR(100);
ALTER TABLE organizations ADD COLUMN headquarters_city VARCHAR(100);
ALTER TABLE organizations ADD COLUMN operating_countries JSONB; -- ["KE", "NG", "ZA", etc.]
ALTER TABLE organizations ADD COLUMN excluded_countries JSONB; -- Countries explicitly excluded

-- New table for detailed country coverage
CREATE TABLE country_funding_metrics (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL UNIQUE,
    country_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL, -- Sub-Saharan, North Africa, etc.
    subregion VARCHAR(50), -- East, West, Central, Southern Africa
    total_opportunities INTEGER DEFAULT 0,
    total_funding_tracked NUMERIC(15,2) DEFAULT 0,
    avg_opportunity_size NUMERIC(12,2),
    last_opportunity_date DATE,
    population BIGINT,
    gdp_per_capita NUMERIC(10,2),
    ai_readiness_score INTEGER, -- 0-100
    digital_infrastructure_score INTEGER, -- 0-100
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add underserved region flags
ALTER TABLE funding_opportunities ADD COLUMN targets_underserved BOOLEAN DEFAULT FALSE;
ALTER TABLE funding_opportunities ADD COLUMN underserved_bonus_points INTEGER DEFAULT 0;
```

### 1.2 Regional Disparity Tracking
```sql
CREATE TABLE regional_funding_gaps (
    id SERIAL PRIMARY KEY,
    region VARCHAR(50) NOT NULL,
    quarter VARCHAR(7) NOT NULL, -- "2024-Q1"
    expected_funding_share NUMERIC(5,2), -- Based on population/GDP
    actual_funding_share NUMERIC(5,2),
    gap_percentage NUMERIC(5,2),
    opportunity_count INTEGER,
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Priority 2: Sectoral Alignment Tracking

### 2.1 Enhanced Sector Classification
```sql
-- Replace or enhance ai_domains with more granular tracking
CREATE TABLE development_sectors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL, -- healthcare, agriculture, education, etc.
    sdg_alignment INTEGER[], -- Array of SDG numbers [3,4,9]
    priority_level INTEGER CHECK (priority_level BETWEEN 1 AND 5),
    description TEXT,
    parent_id INTEGER REFERENCES development_sectors(id)
);

-- Add sectoral tracking to opportunities
ALTER TABLE funding_opportunities 
ADD COLUMN primary_sector_id INTEGER REFERENCES development_sectors(id),
ADD COLUMN secondary_sectors JSONB, -- Array of sector IDs
ADD COLUMN sdg_targets JSONB, -- Specific SDG targets addressed
ADD COLUMN development_impact_score INTEGER CHECK (development_impact_score BETWEEN 0 AND 100);

-- Sector funding metrics
CREATE TABLE sector_funding_metrics (
    id SERIAL PRIMARY KEY,
    sector_id INTEGER REFERENCES development_sectors(id),
    month DATE NOT NULL,
    opportunity_count INTEGER DEFAULT 0,
    total_funding NUMERIC(15,2),
    avg_funding NUMERIC(12,2),
    vs_commercial_ratio NUMERIC(5,2), -- Ratio vs commercial sectors
    UNIQUE(sector_id, month)
);
```

## Priority 3: Gender and Inclusion Analytics

### 3.1 Comprehensive Inclusion Tracking
```sql
CREATE TABLE inclusion_criteria (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE, -- women-led, youth, disabled, rural
    description TEXT,
    tracking_enabled BOOLEAN DEFAULT TRUE
);

-- Junction table for opportunities
CREATE TABLE opportunity_inclusion_criteria (
    opportunity_id INTEGER REFERENCES funding_opportunities(id),
    inclusion_criteria_id INTEGER REFERENCES inclusion_criteria(id),
    is_required BOOLEAN DEFAULT FALSE, -- Required vs encouraged
    bonus_percentage INTEGER, -- Extra points/funding for meeting criteria
    PRIMARY KEY (opportunity_id, inclusion_criteria_id)
);

-- Add to funding_opportunities
ALTER TABLE funding_opportunities 
ADD COLUMN women_led_only BOOLEAN DEFAULT FALSE,
ADD COLUMN youth_focused BOOLEAN DEFAULT FALSE,
ADD COLUMN rural_priority BOOLEAN DEFAULT FALSE,
ADD COLUMN inclusion_score INTEGER DEFAULT 0;

-- Gender funding metrics
CREATE TABLE gender_funding_metrics (
    id SERIAL PRIMARY KEY,
    quarter VARCHAR(7) NOT NULL UNIQUE,
    total_opportunities INTEGER,
    women_focused_opportunities INTEGER,
    women_focused_funding NUMERIC(15,2),
    percentage_of_total NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Priority 4: Funding Stage and Growth Tracking

### 4.1 Detailed Stage Classification
```sql
CREATE TABLE funding_stages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- pre-seed, seed, series-a, growth
    min_amount_usd NUMERIC(12,2),
    max_amount_usd NUMERIC(12,2),
    typical_requirements TEXT,
    success_metrics JSONB
);

ALTER TABLE funding_opportunities 
ADD COLUMN funding_stage_id INTEGER REFERENCES funding_stages(id),
ADD COLUMN min_amount_usd NUMERIC(12,2),
ADD COLUMN max_amount_usd NUMERIC(12,2),
ADD COLUMN requires_matching BOOLEAN DEFAULT FALSE,
ADD COLUMN matching_percentage INTEGER,
ADD COLUMN allows_consortium BOOLEAN DEFAULT FALSE,
ADD COLUMN min_consortium_size INTEGER,
ADD COLUMN max_consortium_size INTEGER;

-- Stage progression tracking
CREATE TABLE funding_stage_transitions (
    id SERIAL PRIMARY KEY,
    organization_name VARCHAR(300),
    from_stage_id INTEGER REFERENCES funding_stages(id),
    to_stage_id INTEGER REFERENCES funding_stages(id),
    transition_date DATE,
    funding_amount NUMERIC(12,2),
    success_factors TEXT
);
```

## Priority 5: Transparency and Accountability Features

### 5.1 Funder Transparency Scoring
```sql
ALTER TABLE organizations 
ADD COLUMN transparency_score INTEGER DEFAULT 50 CHECK (transparency_score BETWEEN 0 AND 100),
ADD COLUMN selection_criteria_public BOOLEAN DEFAULT FALSE,
ADD COLUMN success_rate_public BOOLEAN DEFAULT FALSE,
ADD COLUMN feedback_provided BOOLEAN DEFAULT FALSE,
ADD COLUMN avg_decision_days INTEGER,
ADD COLUMN reporting_burden_score INTEGER CHECK (reporting_burden_score BETWEEN 1 AND 5);

-- Detailed transparency metrics
CREATE TABLE funder_transparency_metrics (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC(5,2),
    measurement_date DATE,
    notes TEXT
);

-- Application feedback tracking
CREATE TABLE application_feedback (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER REFERENCES funding_opportunities(id),
    user_id INTEGER REFERENCES community_users(id),
    applied BOOLEAN DEFAULT FALSE,
    application_date DATE,
    decision VARCHAR(20), -- funded, rejected, withdrawn
    decision_date DATE,
    feedback_quality INTEGER CHECK (feedback_quality BETWEEN 1 AND 5),
    time_to_decision INTEGER, -- days
    reporting_burden INTEGER CHECK (reporting_burden BETWEEN 1 AND 5),
    would_recommend BOOLEAN,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 5.2 Algorithmic Bias Detection
```sql
CREATE TABLE bias_detection_logs (
    id SERIAL PRIMARY KEY,
    analysis_date DATE NOT NULL,
    bias_type VARCHAR(50), -- geographic, gender, sector, language
    affected_entity VARCHAR(200),
    bias_score NUMERIC(5,2), -- Deviation from expected
    sample_size INTEGER,
    corrective_action TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Priority 6: Data Quality and Verification

### 6.1 Enhanced Data Quality Tracking
```sql
ALTER TABLE funding_opportunities 
ADD COLUMN data_quality_score INTEGER DEFAULT 0 CHECK (data_quality_score BETWEEN 0 AND 100),
ADD COLUMN completeness_flags JSONB, -- {"has_deadline": true, "has_amount": false}
ADD COLUMN verification_status VARCHAR(20) DEFAULT 'unverified', -- unverified, community_verified, official_verified
ADD COLUMN verification_date TIMESTAMP,
ADD COLUMN verified_by_user_id INTEGER REFERENCES community_users(id),
ADD COLUMN verification_notes TEXT;

-- Quality improvement tracking
CREATE TABLE data_quality_improvements (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER REFERENCES funding_opportunities(id),
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    improved_by_user_id INTEGER REFERENCES community_users(id),
    improvement_date TIMESTAMP DEFAULT NOW(),
    improvement_source VARCHAR(50) -- community, ai, official
);
```

## Priority 7: Advanced Analytics Support

### 7.1 Predictive Analytics Tables
```sql
CREATE TABLE funding_predictions (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    prediction_type VARCHAR(50), -- next_opportunity, funding_trend
    prediction_date DATE NOT NULL,
    confidence_score NUMERIC(5,2),
    prediction_data JSONB,
    actual_outcome JSONB,
    accuracy_score NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE success_factors (
    id SERIAL PRIMARY KEY,
    factor_name VARCHAR(200) NOT NULL,
    factor_type VARCHAR(50), -- applicant_characteristic, proposal_feature
    correlation_strength NUMERIC(5,2),
    sample_size INTEGER,
    sector_specific BOOLEAN DEFAULT FALSE,
    applicable_sectors JSONB,
    discovered_date DATE,
    validation_status VARCHAR(20)
);
```

### 7.2 Impact Tracking
```sql
CREATE TABLE funded_projects (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER REFERENCES funding_opportunities(id),
    project_name VARCHAR(500),
    lead_organization VARCHAR(300),
    funded_amount NUMERIC(12,2),
    start_date DATE,
    end_date DATE,
    countries_impacted JSONB,
    beneficiaries_count INTEGER,
    jobs_created INTEGER,
    publications_count INTEGER,
    impact_metrics JSONB,
    lessons_learned TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Priority 8: Multi-language and Accessibility

### 8.1 Enhanced Language Support
```sql
CREATE TABLE supported_languages (
    id SERIAL PRIMARY KEY,
    code VARCHAR(5) NOT NULL UNIQUE, -- en, fr, ar, pt, sw
    name VARCHAR(50) NOT NULL,
    native_name VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    translation_quality VARCHAR(20) -- machine, community, professional
);

CREATE TABLE opportunity_translations (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER REFERENCES funding_opportunities(id),
    language_code VARCHAR(5) REFERENCES supported_languages(code),
    title TEXT,
    description TEXT,
    eligibility_criteria TEXT,
    application_instructions TEXT,
    translation_method VARCHAR(20), -- machine, community, professional
    translated_by_user_id INTEGER REFERENCES community_users(id),
    translation_date TIMESTAMP DEFAULT NOW(),
    quality_score INTEGER CHECK (quality_score BETWEEN 1 AND 5),
    UNIQUE(opportunity_id, language_code)
);
```

## Priority 9: Community Features Enhancement

### 9.1 Enhanced Community Engagement
```sql
ALTER TABLE community_users 
ADD COLUMN expertise_areas JSONB,
ADD COLUMN languages_spoken JSONB,
ADD COLUMN country VARCHAR(2),
ADD COLUMN organization_type VARCHAR(50),
ADD COLUMN successful_applications INTEGER DEFAULT 0,
ADD COLUMN mentoring_available BOOLEAN DEFAULT FALSE,
ADD COLUMN karma_score INTEGER DEFAULT 0;

CREATE TABLE community_contributions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES community_users(id),
    contribution_type VARCHAR(50), -- translation, verification, tips, data_improvement
    entity_type VARCHAR(50), -- opportunity, organization
    entity_id INTEGER,
    contribution_date TIMESTAMP DEFAULT NOW(),
    quality_score INTEGER,
    karma_points_earned INTEGER DEFAULT 1
);

CREATE TABLE mentorship_connections (
    id SERIAL PRIMARY KEY,
    mentor_id INTEGER REFERENCES community_users(id),
    mentee_id INTEGER REFERENCES community_users(id),
    opportunity_id INTEGER REFERENCES funding_opportunities(id),
    status VARCHAR(20), -- requested, active, completed
    started_date DATE,
    completed_date DATE,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback TEXT
);
```

## Priority 10: API and Integration Support

### 10.1 API Access Management
```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(256) NOT NULL UNIQUE,
    organization_name VARCHAR(300),
    contact_email VARCHAR(255) NOT NULL,
    use_case TEXT,
    rate_limit INTEGER DEFAULT 1000, -- requests per day
    access_level VARCHAR(20) DEFAULT 'basic', -- basic, premium, internal
    allowed_endpoints JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE api_usage_logs (
    id SERIAL PRIMARY KEY,
    api_key_id INTEGER REFERENCES api_keys(id),
    endpoint VARCHAR(200),
    request_date DATE,
    request_count INTEGER DEFAULT 1,
    data_points_accessed INTEGER,
    response_time_ms INTEGER
);
```

## Implementation Priority Order

1. **Week 1-2**: Geographic equity tables and underserved region tracking
2. **Week 3-4**: Sectoral alignment and development priority tracking  
3. **Week 5-6**: Gender/inclusion analytics and transparency scoring
4. **Week 7-8**: Multi-language support and community features
5. **Week 9-10**: Advanced analytics and API infrastructure
6. **Week 11-12**: Data quality improvements and impact tracking

## Migration Considerations

- All new columns should have sensible defaults to avoid breaking existing code
- Create database views to maintain backward compatibility where needed
- Implement triggers to automatically calculate derived fields (e.g., scores)
- Set up regular jobs to compute aggregate metrics tables
- Consider partitioning large tables by date for better performance