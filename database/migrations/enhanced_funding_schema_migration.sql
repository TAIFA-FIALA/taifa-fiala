-- Enhanced Funding Tracker Schema Migration (Corrected for Existing Schema)
-- Adds comprehensive fields for tracking the three funding announcement patterns
-- Based on actual current schema structure

-- ==========================================
-- Helper Functions
-- ==========================================

-- Function to check if column exists
CREATE OR REPLACE FUNCTION column_exists(p_table_name text, p_column_name text)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = p_table_name 
        AND column_name = p_column_name
    );
END;
$$ LANGUAGE plpgsql;

-- Function to check if index exists
CREATE OR REPLACE FUNCTION index_exists(p_index_name text)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE indexname = p_index_name
    );
END;
$$ LANGUAGE plpgsql;

-- Function to check if constraint exists
CREATE OR REPLACE FUNCTION constraint_exists(p_constraint_name text, p_table_name text DEFAULT NULL)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE 
            (p_table_name IS NULL OR table_name = p_table_name) 
            AND constraint_name = p_constraint_name
    );
END;
$$ LANGUAGE plpgsql;


-- ==========================================
-- Add Enhanced Funding Fields
-- ==========================================

-- Add enhanced funding amount fields to support all three patterns
DO $$
BEGIN
    -- Total funding pool for "total_pool" type
    IF NOT column_exists('africa_intelligence_feed', 'total_funding_pool') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN total_funding_pool NUMERIC(15,2);
        RAISE NOTICE 'Added column: total_funding_pool';
    END IF;
    
    -- Enhanced funding type field (update existing if needed)
    IF column_exists('africa_intelligence_feed', 'funding_type') THEN
        -- Update constraint if it exists
        BEGIN
            ALTER TABLE africa_intelligence_feed DROP CONSTRAINT IF EXISTS chk_funding_type;
            ALTER TABLE africa_intelligence_feed ADD CONSTRAINT chk_funding_type 
                CHECK (funding_type IN ('total_pool', 'per_project_exact', 'per_project_range', 'general', 'opportunity'));
            RAISE NOTICE 'Updated funding_type constraint';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not update funding_type constraint: %', SQLERRM;
        END;
        
        -- Set default value for existing null records
        UPDATE africa_intelligence_feed 
        SET funding_type = 'per_project_range' 
        WHERE funding_type IS NULL OR funding_type = '';
    END IF;
    
    -- Min/max amounts per project
    IF NOT column_exists('africa_intelligence_feed', 'min_amount_per_project') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN min_amount_per_project NUMERIC(15,2);
        RAISE NOTICE 'Added column: min_amount_per_project';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'max_amount_per_project') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN max_amount_per_project NUMERIC(15,2);
        RAISE NOTICE 'Added column: max_amount_per_project';
    END IF;
    
    -- Exact amount per project
    IF NOT column_exists('africa_intelligence_feed', 'exact_amount_per_project') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN exact_amount_per_project NUMERIC(15,2);
        RAISE NOTICE 'Added column: exact_amount_per_project';
    END IF;
    
    -- Project count fields
    IF NOT column_exists('africa_intelligence_feed', 'estimated_project_count') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN estimated_project_count INTEGER;
        RAISE NOTICE 'Added column: estimated_project_count';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'project_count_range') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN project_count_range JSONB;
        RAISE NOTICE 'Added column: project_count_range';
    END IF;
END $$;

-- ==========================================
-- Add Enhanced Timing and Process Fields
-- ==========================================

DO $$
BEGIN
    -- Application deadline type
    IF NOT column_exists('africa_intelligence_feed', 'application_deadline_type') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN application_deadline_type VARCHAR(20) DEFAULT 'fixed';
        ALTER TABLE africa_intelligence_feed ADD CONSTRAINT chk_application_deadline_type 
            CHECK (application_deadline_type IN ('rolling', 'fixed', 'multiple_rounds'));
        RAISE NOTICE 'Added column: application_deadline_type';
    END IF;
    
    -- Announcement and funding dates
    IF NOT column_exists('africa_intelligence_feed', 'announcement_date') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN announcement_date DATE;
        RAISE NOTICE 'Added column: announcement_date';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'funding_start_date') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN funding_start_date DATE;
        RAISE NOTICE 'Added column: funding_start_date';
    END IF;
    
    -- Project duration
    IF NOT column_exists('africa_intelligence_feed', 'project_duration') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN project_duration VARCHAR(100);
        RAISE NOTICE 'Added column: project_duration';
    END IF;
    
    -- Selection criteria (application_process already exists)
    IF NOT column_exists('africa_intelligence_feed', 'selection_criteria') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN selection_criteria JSONB;
        RAISE NOTICE 'Added column: selection_criteria';
    END IF;
END $$;

-- ==========================================
-- Add Enhanced Targeting and Focus Fields
-- ==========================================

DO $$
BEGIN
    -- Target audience
    IF NOT column_exists('africa_intelligence_feed', 'target_audience') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN target_audience JSONB;
        RAISE NOTICE 'Added column: target_audience';
    END IF;
    
    -- AI subsectors
    IF NOT column_exists('africa_intelligence_feed', 'ai_subsectors') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN ai_subsectors JSONB;
        RAISE NOTICE 'Added column: ai_subsectors';
    END IF;
    
    -- Development stage
    IF NOT column_exists('africa_intelligence_feed', 'development_stage') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN development_stage JSONB;
        RAISE NOTICE 'Added column: development_stage';
    END IF;
    
    -- Collaboration required
    IF NOT column_exists('africa_intelligence_feed', 'collaboration_required') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN collaboration_required BOOLEAN;
        RAISE NOTICE 'Added column: collaboration_required';
    END IF;
    
    -- Gender focused (use existing women_focus or create new)
    IF NOT column_exists('africa_intelligence_feed', 'gender_focused') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN gender_focused BOOLEAN;
        -- Copy data from existing women_focus column
        UPDATE africa_intelligence_feed SET gender_focused = women_focus WHERE women_focus IS NOT NULL;
        RAISE NOTICE 'Added column: gender_focused (copied from women_focus)';
    END IF;
    
    -- Youth focused (use existing youth_focus or create new)
    IF NOT column_exists('africa_intelligence_feed', 'youth_focused') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN youth_focused BOOLEAN;
        -- Copy data from existing youth_focus column
        UPDATE africa_intelligence_feed SET youth_focused = youth_focus WHERE youth_focus IS NOT NULL;
        RAISE NOTICE 'Added column: youth_focused (copied from youth_focus)';
    END IF;
END $$;

-- ==========================================
-- Add Enhanced Reporting Fields
-- ==========================================

DO $$
BEGIN
    -- Enhanced reporting requirements (as JSONB for structured data)
    IF NOT column_exists('africa_intelligence_feed', 'reporting_requirements') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN reporting_requirements JSONB;
        RAISE NOTICE 'Added column: reporting_requirements';
    END IF;
    
    -- Enhanced grant-specific fields
    IF NOT column_exists('africa_intelligence_feed', 'interim_reporting_required') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN interim_reporting_required BOOLEAN;
        RAISE NOTICE 'Added column: interim_reporting_required';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'final_report_required') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN final_report_required BOOLEAN;
        RAISE NOTICE 'Added column: final_report_required';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'financial_reporting_frequency') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN financial_reporting_frequency VARCHAR(20);
        ALTER TABLE africa_intelligence_feed ADD CONSTRAINT chk_financial_reporting_frequency 
            CHECK (financial_reporting_frequency IN ('monthly', 'quarterly', 'annually'));
        RAISE NOTICE 'Added column: financial_reporting_frequency';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'intellectual_property_rights') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN intellectual_property_rights TEXT;
        RAISE NOTICE 'Added column: intellectual_property_rights';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'publication_requirements') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN publication_requirements TEXT;
        RAISE NOTICE 'Added column: publication_requirements';
    END IF;
END $$;

-- ==========================================
-- Add Enhanced Investment-Specific Fields
-- ==========================================

DO $$
BEGIN
    -- Enhanced investment fields
    IF NOT column_exists('africa_intelligence_feed', 'liquidation_preference') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN liquidation_preference TEXT;
        RAISE NOTICE 'Added column: liquidation_preference';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'board_representation') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN board_representation BOOLEAN;
        RAISE NOTICE 'Added column: board_representation';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'anti_dilution_protection') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN anti_dilution_protection TEXT;
        RAISE NOTICE 'Added column: anti_dilution_protection';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'drag_along_rights') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN drag_along_rights BOOLEAN;
        RAISE NOTICE 'Added column: drag_along_rights';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'tag_along_rights') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN tag_along_rights BOOLEAN;
        RAISE NOTICE 'Added column: tag_along_rights';
    END IF;
END $$;

-- ==========================================
-- Add Prize/Competition-Specific Fields
-- ==========================================

DO $$
BEGIN
    -- Prize and competition fields
    IF NOT column_exists('africa_intelligence_feed', 'competition_phases') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN competition_phases JSONB;
        RAISE NOTICE 'Added column: competition_phases';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'judging_criteria') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN judging_criteria JSONB;
        RAISE NOTICE 'Added column: judging_criteria';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'submission_format') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN submission_format TEXT;
        RAISE NOTICE 'Added column: submission_format';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'presentation_required') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN presentation_required BOOLEAN;
        RAISE NOTICE 'Added column: presentation_required';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'team_size_limit') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN team_size_limit INTEGER;
        RAISE NOTICE 'Added column: team_size_limit';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'intellectual_property_ownership') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN intellectual_property_ownership TEXT;
        RAISE NOTICE 'Added column: intellectual_property_ownership';
    END IF;
END $$;

-- ==========================================
-- Add Enhanced Metadata Fields
-- ==========================================

DO $$
BEGIN
    -- Urgency and deadline tracking
    IF NOT column_exists('africa_intelligence_feed', 'urgency_level') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN urgency_level VARCHAR(10);
        ALTER TABLE africa_intelligence_feed ADD CONSTRAINT chk_urgency_level 
            CHECK (urgency_level IN ('urgent', 'moderate', 'low', 'expired', 'unknown'));
        RAISE NOTICE 'Added column: urgency_level';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'days_until_deadline') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN days_until_deadline INTEGER;
        RAISE NOTICE 'Added column: days_until_deadline';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'is_deadline_approaching') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN is_deadline_approaching BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added column: is_deadline_approaching';
    END IF;
    
    -- Suitability indicators
    IF NOT column_exists('africa_intelligence_feed', 'suitable_for_startups') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN suitable_for_startups BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added column: suitable_for_startups';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'suitable_for_researchers') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN suitable_for_researchers BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added column: suitable_for_researchers';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'suitable_for_smes') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN suitable_for_smes BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added column: suitable_for_smes';
    END IF;
    
    IF NOT column_exists('africa_intelligence_feed', 'suitable_for_individuals') THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN suitable_for_individuals BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added column: suitable_for_individuals';
    END IF;
END $$;

-- ==========================================
-- Create Enhanced Indexes
-- ==========================================

DO $$
BEGIN
    -- Indexes for enhanced funding fields
    IF NOT index_exists('idx_africa_intelligence_funding_type_enhanced') THEN
        CREATE INDEX idx_africa_intelligence_funding_type_enhanced ON africa_intelligence_feed(funding_type);
        RAISE NOTICE 'Created index: idx_africa_intelligence_funding_type_enhanced';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_total_funding_pool') THEN
        CREATE INDEX idx_africa_intelligence_total_funding_pool ON africa_intelligence_feed(total_funding_pool);
        RAISE NOTICE 'Created index: idx_africa_intelligence_total_funding_pool';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_min_amount_per_project') THEN
        CREATE INDEX idx_africa_intelligence_min_amount_per_project ON africa_intelligence_feed(min_amount_per_project);
        RAISE NOTICE 'Created index: idx_africa_intelligence_min_amount_per_project';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_max_amount_per_project') THEN
        CREATE INDEX idx_africa_intelligence_max_amount_per_project ON africa_intelligence_feed(max_amount_per_project);
        RAISE NOTICE 'Created index: idx_africa_intelligence_max_amount_per_project';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_exact_amount_per_project') THEN
        CREATE INDEX idx_africa_intelligence_exact_amount_per_project ON africa_intelligence_feed(exact_amount_per_project);
        RAISE NOTICE 'Created index: idx_africa_intelligence_exact_amount_per_project';
    END IF;
    
    -- Indexes for targeting fields
    IF NOT index_exists('idx_africa_intelligence_collaboration_required') THEN
        CREATE INDEX idx_africa_intelligence_collaboration_required ON africa_intelligence_feed(collaboration_required);
        RAISE NOTICE 'Created index: idx_africa_intelligence_collaboration_required';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_gender_focused') THEN
        CREATE INDEX idx_africa_intelligence_gender_focused ON africa_intelligence_feed(gender_focused);
        RAISE NOTICE 'Created index: idx_africa_intelligence_gender_focused';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_youth_focused') THEN
        CREATE INDEX idx_africa_intelligence_youth_focused ON africa_intelligence_feed(youth_focused);
        RAISE NOTICE 'Created index: idx_africa_intelligence_youth_focused';
    END IF;
    
    -- Indexes for timing fields
    IF NOT index_exists('idx_africa_intelligence_application_deadline_type') THEN
        CREATE INDEX idx_africa_intelligence_application_deadline_type ON africa_intelligence_feed(application_deadline_type);
        RAISE NOTICE 'Created index: idx_africa_intelligence_application_deadline_type';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_funding_start_date') THEN
        CREATE INDEX idx_africa_intelligence_funding_start_date ON africa_intelligence_feed(funding_start_date);
        RAISE NOTICE 'Created index: idx_africa_intelligence_funding_start_date';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_urgency_level') THEN
        CREATE INDEX idx_africa_intelligence_urgency_level ON africa_intelligence_feed(urgency_level);
        RAISE NOTICE 'Created index: idx_africa_intelligence_urgency_level';
    END IF;
    
    -- JSON indexes for enhanced arrays
    IF NOT index_exists('idx_africa_intelligence_target_audience_gin') THEN
        CREATE INDEX idx_africa_intelligence_target_audience_gin ON africa_intelligence_feed USING gin(target_audience);
        RAISE NOTICE 'Created index: idx_africa_intelligence_target_audience_gin';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_ai_subsectors_gin') THEN
        CREATE INDEX idx_africa_intelligence_ai_subsectors_gin ON africa_intelligence_feed USING gin(ai_subsectors);
        RAISE NOTICE 'Created index: idx_africa_intelligence_ai_subsectors_gin';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_development_stage_gin') THEN
        CREATE INDEX idx_africa_intelligence_development_stage_gin ON africa_intelligence_feed USING gin(development_stage);
        RAISE NOTICE 'Created index: idx_africa_intelligence_development_stage_gin';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_selection_criteria_gin') THEN
        CREATE INDEX idx_africa_intelligence_selection_criteria_gin ON africa_intelligence_feed USING gin(selection_criteria);
        RAISE NOTICE 'Created index: idx_africa_intelligence_selection_criteria_gin';
    END IF;
    
    IF NOT index_exists('idx_africa_intelligence_reporting_requirements_gin') THEN
        CREATE INDEX idx_africa_intelligence_reporting_requirements_gin ON africa_intelligence_feed USING gin(reporting_requirements);
        RAISE NOTICE 'Created index: idx_africa_intelligence_reporting_requirements_gin';
    END IF;
END $$;

-- ==========================================
-- Create Enhanced Views
-- ==========================================

-- View for funding opportunities by type
CREATE OR REPLACE VIEW funding_opportunities_by_type AS
SELECT 
    funding_type,
    COUNT(*) as opportunity_count,
    AVG(CASE 
        WHEN funding_type = 'total_pool' THEN total_funding_pool
        WHEN funding_type = 'per_project_exact' THEN exact_amount_per_project
        WHEN funding_type = 'per_project_range' THEN (COALESCE(min_amount_per_project, 0) + COALESCE(max_amount_per_project, 0)) / 2
        WHEN amount_exact IS NOT NULL THEN amount_exact
        WHEN amount_min IS NOT NULL AND amount_max IS NOT NULL THEN (amount_min + amount_max) / 2
    END) as avg_funding_amount,
    SUM(CASE 
        WHEN funding_type = 'total_pool' THEN total_funding_pool
        WHEN funding_type = 'per_project_exact' THEN exact_amount_per_project * COALESCE(estimated_project_count, 1)
        WHEN funding_type = 'per_project_range' THEN ((COALESCE(min_amount_per_project, 0) + COALESCE(max_amount_per_project, 0)) / 2) * COALESCE(estimated_project_count, 1)
        WHEN amount_exact IS NOT NULL THEN amount_exact
        WHEN amount_min IS NOT NULL AND amount_max IS NOT NULL THEN (amount_min + amount_max) / 2
    END) as total_funding_available
FROM africa_intelligence_feed
WHERE status IS NULL OR status != 'inactive'
GROUP BY funding_type;

-- View for urgent opportunities
CREATE OR REPLACE VIEW urgent_funding_opportunities AS
SELECT 
    id,
    title,
    COALESCE(
        (SELECT name FROM organizations WHERE id = provider_organization_id LIMIT 1),
        'Unknown Organization'
    ) as organization_name,
    funding_type,
    CASE 
        WHEN funding_type = 'total_pool' THEN total_funding_pool::TEXT
        WHEN funding_type = 'per_project_exact' THEN exact_amount_per_project::TEXT
        WHEN funding_type = 'per_project_range' THEN 
            COALESCE(min_amount_per_project::TEXT, '') || ' - ' || COALESCE(max_amount_per_project::TEXT, '')
        WHEN amount_exact IS NOT NULL THEN amount_exact::TEXT
        WHEN amount_min IS NOT NULL OR amount_max IS NOT NULL THEN 
            COALESCE(amount_min::TEXT, '') || ' - ' || COALESCE(amount_max::TEXT, '')
        ELSE 'Amount not specified'
    END as funding_amount_display,
    application_deadline,
    urgency_level,
    days_until_deadline,
    application_deadline_type,
    gender_focused,
    youth_focused,
    collaboration_required,
    currency
FROM africa_intelligence_feed
WHERE (status IS NULL OR status != 'inactive')
  AND application_deadline >= CURRENT_DATE
  AND urgency_level IN ('urgent', 'moderate')
ORDER BY urgency_level = 'urgent' DESC, days_until_deadline ASC;

-- ==========================================
-- Create Enhanced Functions
-- ==========================================

-- Function to calculate urgency level
CREATE OR REPLACE FUNCTION calculate_urgency_level(deadline_date DATE)
RETURNS VARCHAR(10) AS $$
BEGIN
    IF deadline_date IS NULL THEN
        RETURN 'unknown';
    END IF;
    
    RETURN CASE 
        WHEN deadline_date < CURRENT_DATE THEN 'expired'
        WHEN deadline_date - CURRENT_DATE <= 7 THEN 'urgent'
        WHEN deadline_date - CURRENT_DATE <= 30 THEN 'moderate'
        ELSE 'low'
    END;
END;
$$ LANGUAGE plpgsql;

-- Function to update urgency fields
CREATE OR REPLACE FUNCTION update_urgency_fields()
RETURNS TRIGGER AS $$
BEGIN
    NEW.urgency_level := calculate_urgency_level(NEW.application_deadline);
    NEW.days_until_deadline := CASE 
        WHEN NEW.application_deadline IS NOT NULL THEN (NEW.application_deadline - CURRENT_DATE)
        ELSE NULL
    END;
    NEW.is_deadline_approaching := CASE
        WHEN NEW.application_deadline IS NOT NULL AND NEW.application_deadline - CURRENT_DATE BETWEEN 0 AND 30 THEN TRUE
        ELSE FALSE
    END;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to determine suitability flags
CREATE OR REPLACE FUNCTION update_suitability_flags()
RETURNS TRIGGER AS $$
BEGIN
    -- Reset flags
    NEW.suitable_for_startups := FALSE;
    NEW.suitable_for_researchers := FALSE;
    NEW.suitable_for_smes := FALSE;
    NEW.suitable_for_individuals := FALSE;
    
    -- Check target audience
    IF NEW.target_audience IS NOT NULL THEN
        NEW.suitable_for_startups := NEW.target_audience ? 'startups' OR NEW.target_audience ? 'entrepreneurs';
        NEW.suitable_for_researchers := NEW.target_audience ? 'researchers' OR NEW.target_audience ? 'academics';
        NEW.suitable_for_smes := NEW.target_audience ? 'smes' OR NEW.target_audience ? 'small businesses';
        NEW.suitable_for_individuals := NEW.target_audience ? 'individuals' OR NEW.target_audience ? 'freelancers';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- Create Triggers
-- ==========================================

-- Create trigger to automatically update urgency fields
DROP TRIGGER IF EXISTS trigger_update_urgency_fields ON africa_intelligence_feed;
CREATE TRIGGER trigger_update_urgency_fields
    BEFORE INSERT OR UPDATE OF application_deadline
    ON africa_intelligence_feed
    FOR EACH ROW
    EXECUTE FUNCTION update_urgency_fields();

-- Create trigger to automatically update suitability flags
DROP TRIGGER IF EXISTS trigger_update_suitability_flags ON africa_intelligence_feed;
CREATE TRIGGER trigger_update_suitability_flags
    BEFORE INSERT OR UPDATE OF target_audience
    ON africa_intelligence_feed
    FOR EACH ROW
    EXECUTE FUNCTION update_suitability_flags();

-- ==========================================
-- Data Migration for Existing Records
-- ==========================================

-- Migrate existing amount data to new enhanced fields
DO $$
BEGIN
    RAISE NOTICE 'Starting data migration for existing records...';
    
    -- Copy existing amount data to new fields based on current data
    UPDATE africa_intelligence_feed 
    SET 
        min_amount_per_project = amount_min,
        max_amount_per_project = amount_max,
        exact_amount_per_project = amount_exact
    WHERE min_amount_per_project IS NULL;
    
    -- Set funding_type based on existing amount fields
    UPDATE africa_intelligence_feed 
    SET funding_type = CASE
        WHEN amount_exact IS NOT NULL OR exact_amount_per_project IS NOT NULL THEN 'per_project_exact'
        WHEN amount_min IS NOT NULL AND amount_max IS NOT NULL THEN 'per_project_range'
        WHEN funding_type IN ('total_pool', 'per_project_exact', 'per_project_range') THEN funding_type
        ELSE 'per_project_range'
    END
    WHERE funding_type IS NULL OR funding_type NOT IN ('total_pool', 'per_project_exact', 'per_project_range');
    
    -- Update urgency levels for existing records
    UPDATE africa_intelligence_feed 
    SET 
        urgency_level = calculate_urgency_level(application_deadline),
        days_until_deadline = CASE 
            WHEN application_deadline IS NOT NULL THEN (application_deadline - CURRENT_DATE)
            ELSE NULL
        END,
        is_deadline_approaching = CASE
            WHEN application_deadline IS NOT NULL AND application_deadline - CURRENT_DATE BETWEEN 0 AND 30 THEN TRUE
            ELSE FALSE
        END
    WHERE urgency_level IS NULL;
    
    -- Copy focus data from existing columns
    UPDATE africa_intelligence_feed 
    SET gender_focused = women_focus 
    WHERE gender_focused IS NULL AND women_focus IS NOT NULL;
    
    UPDATE africa_intelligence_feed 
    SET youth_focused = youth_focus 
    WHERE youth_focused IS NULL AND youth_focus IS NOT NULL;
    
    RAISE NOTICE 'Data migration completed successfully.';
END $$;

-- ==========================================
-- Clean up helper functions
-- ==========================================

DROP FUNCTION IF EXISTS column_exists(text, text);
DROP FUNCTION IF EXISTS index_exists(text);

-- ==========================================
-- Comments for Documentation
-- ==========================================

COMMENT ON COLUMN africa_intelligence_feed.funding_type IS 'Enhanced: total_pool (total available), per_project_exact (fixed amount per project), per_project_range (range per project)';
COMMENT ON COLUMN africa_intelligence_feed.total_funding_pool IS 'Total funding available for disbursement (for total_pool type)';
COMMENT ON COLUMN africa_intelligence_feed.min_amount_per_project IS 'Minimum funding amount per project (for per_project_range type)';
COMMENT ON COLUMN africa_intelligence_feed.max_amount_per_project IS 'Maximum funding amount per project (for per_project_range type)';
COMMENT ON COLUMN africa_intelligence_feed.exact_amount_per_project IS 'Fixed funding amount per project (for per_project_exact type)';
COMMENT ON COLUMN africa_intelligence_feed.estimated_project_count IS 'Estimated or announced number of projects to be funded';
COMMENT ON COLUMN africa_intelligence_feed.project_count_range IS 'Range of projects to be funded: {"min": int, "max": int}';
COMMENT ON COLUMN africa_intelligence_feed.target_audience IS 'JSON array of target audience types: startups, researchers, smes, individuals, etc.';
COMMENT ON COLUMN africa_intelligence_feed.ai_subsectors IS 'JSON array of specific AI focus areas';
COMMENT ON COLUMN africa_intelligence_feed.urgency_level IS 'Calculated urgency based on deadline: urgent, moderate, low, expired, unknown';

RAISE NOTICE '✅ Enhanced funding schema migration completed successfully!';
