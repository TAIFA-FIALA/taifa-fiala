-- Migration to add all required columns for FundingOpportunityCard
-- Handles existing columns gracefully

-- Add renewable column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'renewable'
    ) THEN
        ALTER TABLE africa_intelligence_feed 
        ADD COLUMN renewable BOOLEAN DEFAULT NULL;
        
        RAISE NOTICE 'Added column: renewable';
    END IF;
END $$;

-- Add other required columns with the same pattern
DO $$
BEGIN
    -- Add is_active if it doesn't exist
    -- This indicates if the funding call is currently active (posted but not yet closed)
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'is_active'
    ) THEN
        -- Add the column first
        ALTER TABLE africa_intelligence_feed 
        ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
        
        -- Update the column based on current data
        UPDATE africa_intelligence_feed 
        SET is_active = (
            CASE 
                WHEN application_deadline IS NULL THEN (status = 'active')
                WHEN status = 'active' AND application_deadline >= CURRENT_DATE THEN TRUE
                ELSE FALSE
            END
        );
        
        RAISE NOTICE 'Added column: is_active (active when status=active and deadline is in future)';
    END IF;
    
    -- Add is_accepting_applications if it doesn't exist
    -- This indicates if the funding call is currently accepting applications (based on deadline)
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'is_accepting_applications'
    ) THEN
        -- Add the column first
        ALTER TABLE africa_intelligence_feed 
        ADD COLUMN is_accepting_applications BOOLEAN DEFAULT TRUE;
        
        -- Update the column based on current data
        UPDATE africa_intelligence_feed 
        SET is_accepting_applications = (
            CASE 
                WHEN application_deadline IS NULL THEN TRUE
                WHEN application_deadline >= CURRENT_DATE THEN TRUE
                ELSE FALSE
            END
        );
        
        RAISE NOTICE 'Added column: is_accepting_applications';
    END IF;
    
    -- Note: is_public_application is derived from eligibility_criteria text
    
    -- Add requires_registration if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'requires_registration'
    ) THEN
        ALTER TABLE africa_intelligence_feed 
        ADD COLUMN requires_registration BOOLEAN DEFAULT TRUE;
        
        RAISE NOTICE 'Added column: requires_registration';
    END IF;
END $$;
