-- Create or replace function to update the computed columns
CREATE OR REPLACE FUNCTION public.update_funding_opportunity_status()
RETURNS TRIGGER AS $$
BEGIN
    NEW.is_active := (
        CASE 
            WHEN NEW.application_deadline IS NULL THEN (NEW.status = 'active')
            WHEN NEW.status = 'active' AND NEW.application_deadline >= CURRENT_DATE THEN TRUE
            ELSE FALSE
        END
    );
    
    NEW.is_accepting_applications := (
        CASE 
            WHEN NEW.application_deadline IS NULL THEN TRUE
            WHEN NEW.application_deadline >= CURRENT_DATE THEN TRUE
            ELSE FALSE
        END
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create or replace the trigger
DROP TRIGGER IF EXISTS trg_update_funding_opportunity_status ON public.africa_intelligence_feed;
CREATE TRIGGER trg_update_funding_opportunity_status
BEFORE INSERT OR UPDATE OF status, application_deadline
ON public.africa_intelligence_feed
FOR EACH ROW
EXECUTE FUNCTION public.update_funding_opportunity_status();

-- Check if columns exist before updating
DO $$
BEGIN
    -- Check if is_active column exists
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'africa_intelligence_feed' 
        AND column_name = 'is_active'
    ) AND EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'africa_intelligence_feed' 
        AND column_name = 'is_accepting_applications'
    ) THEN
        -- Update existing records to set initial values
        EXECUTE '
        UPDATE public.africa_intelligence_feed 
        SET 
            is_active = (
                CASE 
                    WHEN application_deadline IS NULL THEN (status = ''active'')
                    WHEN status = ''active'' AND application_deadline >= CURRENT_DATE THEN TRUE
                    ELSE FALSE
                END
            ),
            is_accepting_applications = (
                CASE 
                    WHEN application_deadline IS NULL THEN TRUE
                    WHEN application_deadline >= CURRENT_DATE THEN TRUE
                    ELSE FALSE
                END
            )
        WHERE is_active IS NULL OR is_accepting_applications IS NULL;';
        
        RAISE NOTICE 'Updated existing records with initial values for is_active and is_accepting_applications';
    ELSE
        RAISE NOTICE 'Skipping update: Required columns do not exist. Please run the column migration first.';
    END IF;
END $$;
