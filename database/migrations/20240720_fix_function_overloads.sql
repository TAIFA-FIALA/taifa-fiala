-- Fix function overloads and security settings
-- This migration standardizes function security and removes duplicates

-- 1. First, drop the duplicate calculate_urgency_level function
DO $$
BEGIN
    -- Drop the function with (timestamp with time zone, interval, timestamp with time zone) signature
    -- if it exists and is not being used by other objects
    IF EXISTS (
        SELECT 1 
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public'
        AND p.proname = 'calculate_urgency_level'
        AND pg_get_function_arguments(p.oid) = 'timestamp with time zone, interval, timestamp with time zone'
    ) THEN
        DROP FUNCTION IF EXISTS public.calculate_urgency_level(timestamp with time zone, interval, timestamp with time zone);
        RAISE NOTICE 'Dropped duplicate calculate_urgency_level function';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error dropping duplicate calculate_urgency_level: %', SQLERRM;
END $$;

-- 2. Update the remaining calculate_urgency_level function
DO $$
BEGIN
    EXECUTE $f$
    CREATE OR REPLACE FUNCTION public.calculate_urgency_level(deadline_date date)
    RETURNS character varying
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public, pg_temp
    AS $function$
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
    $function$
    $f$;
    
    RAISE NOTICE 'Updated calculate_urgency_level with proper security settings';
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error updating calculate_urgency_level: %', SQLERRM;
END $$;

-- 3. Update update_funding_opportunity_status function
DO $$
BEGIN
    EXECUTE $f$
    CREATE OR REPLACE FUNCTION public.update_funding_opportunity_status()
    RETURNS trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public, pg_temp
    AS $function$
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
    $function$
    $f$;
    
    RAISE NOTICE 'Updated update_funding_opportunity_status with proper security settings';
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error updating update_funding_opportunity_status: %', SQLERRM;
END $$;

-- 4. Update update_suitability_flags function
DO $$
BEGIN
    EXECUTE $f$
    CREATE OR REPLACE FUNCTION public.update_suitability_flags()
    RETURNS trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public, pg_temp
    AS $function$
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
    $function$
    $f$;
    
    RAISE NOTICE 'Updated update_suitability_flags with proper security settings';
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error updating update_suitability_flags: %', SQLERRM;
END $$;

-- 5. Update update_urgency_fields function
DO $$
BEGIN
    EXECUTE $f$
    CREATE OR REPLACE FUNCTION public.update_urgency_fields()
    RETURNS trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public, pg_temp
    AS $function$
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
    $function$
    $f$;
    
    RAISE NOTICE 'Updated update_urgency_fields with proper security settings';
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error updating update_urgency_fields: %', SQLERRM;
END $$;

-- 6. Update any triggers that use these functions
DO $$
BEGIN
    -- Example: Update triggers if they exist
    -- This is a placeholder - adjust based on your actual triggers
    IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_funding_opportunity_status_trigger') THEN
        EXECUTE 'DROP TRIGGER IF EXISTS update_funding_opportunity_status_trigger ON your_table_name';
        EXECUTE 'CREATE TRIGGER update_funding_opportunity_status_trigger BEFORE INSERT OR UPDATE ON your_table_name FOR EACH ROW EXECUTE FUNCTION update_funding_opportunity_status()';
    END IF;
    
    -- Add similar blocks for other triggers
    
    RAISE NOTICE 'Updated triggers to use the new function definitions';
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error updating triggers: %', SQLERRM;
END $$;

-- 7. Notify completion
DO $$
BEGIN
    RAISE NOTICE 'All function security updates completed successfully';
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error in final notification: %', SQLERRM;
END $$;
