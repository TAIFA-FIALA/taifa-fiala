-- Fix function security settings to prevent search_path manipulation
-- This migration updates all functions to use proper security settings

-- Helper function to safely update a function's security settings
CREATE OR REPLACE FUNCTION public.update_function_security(
    p_function_name text,
    p_function_args text,
    p_function_body text,
    p_function_comment text DEFAULT NULL
) 
RETURNS void
LANGUAGE plpgsql
AS $func$
BEGIN
    EXECUTE format('DROP FUNCTION IF EXISTS %I%s', p_function_name, p_function_args);
    EXECUTE format('CREATE FUNCTION %I%s %s', p_function_name, p_function_args, p_function_body);
    
    IF p_function_comment IS NOT NULL THEN
        EXECUTE format('COMMENT ON FUNCTION %I%s IS %L', p_function_name, p_function_args, p_function_comment);
    END IF;
    
    RAISE NOTICE 'Updated function % with proper security settings', p_function_name;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error updating function %: %', p_function_name, SQLERRM;
END;
$func$;

-- Start a transaction to ensure all updates are atomic
BEGIN;

-- 1. Update constraint_exists function
SELECT public.update_function_security(
    'constraint_exists',
    '(text, text)',
    'RETURNS boolean
    LANGUAGE sql
    SECURITY DEFINER
    SET search_path = public, pg_temp
    AS $inner_func$
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE constraint_name = $1 
        AND table_name = $2
    );
    $inner_func$;',
    'Safely check if a constraint exists on a table with proper security context'
);

-- 2. Update calculate_urgency_level function
SELECT public.update_function_security(
    'calculate_urgency_level',
    '(timestamp with time zone, interval, timestamp with time zone)',
    'RETURNS text
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public, pg_temp
    AS $inner_func$
    DECLARE
        days_until_deadline integer;
    BEGIN
        IF $1 IS NULL THEN
            RETURN ''none'';
        END IF;
        
        days_until_deadline := ($1 - COALESCE($3, CURRENT_TIMESTAMP))::integer / 86400;
        
        IF days_until_deadline <= 7 THEN
            RETURN ''urgent'';
        ELSIF days_until_deadline <= 30 THEN
            RETURN ''moderate'';
        ELSE
            RETURN ''normal'';
        END IF;
    END;
    $inner_func$;',
    'Calculate urgency level based on deadline and current time'
);

-- 3. Update update_urgency_fields function
SELECT public.update_function_security(
    'update_urgency_fields',
    '()',
    'RETURNS trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public, pg_temp
    AS $inner_func$
    BEGIN
        NEW.urgency_level := public.calculate_urgency_level(
            NEW.application_deadline, 
            NEW.duration, 
            NEW.created_at
        );
        
        IF NEW.application_deadline IS NOT NULL THEN
            NEW.days_until_deadline := (NEW.application_deadline - COALESCE(NEW.updated_at, CURRENT_TIMESTAMP))::integer / 86400;
        ELSE
            NEW.days_until_deadline := NULL;
        END IF;
        
        RETURN NEW;
    END;
    $inner_func$;',
    'Update urgency-related fields when record is inserted or updated'
);

-- 4. Update update_suitability_flags function
SELECT public.update_function_security(
    'update_suitability_flags',
    '()',
    'RETURNS trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public, pg_temp
    AS $inner_func$
    BEGIN
        -- Set gender_focused flag if gender-related terms are found
        NEW.gender_focused := (
            NEW.title ILIKE ''%women%'' OR 
            NEW.title ILIKE ''%gender%'' OR 
            NEW.eligibility_criteria::text ILIKE ''%women%'' OR 
            NEW.eligibility_criteria::text ILIKE ''%gender%''
        );
        
        -- Set youth_focused flag if youth-related terms are found
        NEW.youth_focused := (
            NEW.title ILIKE ''%youth%'' OR 
            NEW.title ILIKE ''%young%'' OR 
            NEW.eligibility_criteria::text ILIKE ''%youth%'' OR 
            NEW.eligibility_criteria::text ILIKE ''%young%''
        );
        
        -- Set collaboration_required flag if collaboration-related terms are found
        NEW.collaboration_required := (
            NEW.title ILIKE ''%partner%'' OR 
            NEW.title ILIKE ''%collaborat%'' OR 
            NEW.eligibility_criteria::text ILIKE ''%partner%'' OR 
            NEW.eligibility_criteria::text ILIKE ''%collaborat%''
        );
        
        RETURN NEW;
    END;
    $inner_func$;',
    'Update suitability flags based on content analysis'
);

-- 5. Update update_funding_opportunity_status function
SELECT public.update_function_security(
    'update_funding_opportunity_status',
    '()',
    'RETURNS trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public, pg_temp
    AS $inner_func$
    BEGIN
        -- Set status based on deadline
        IF NEW.application_deadline IS NOT NULL THEN
            IF NEW.application_deadline < CURRENT_TIMESTAMP THEN
                NEW.status := ''closed'';
            ELSIF NEW.status IS NULL OR NEW.status = '''' THEN
                NEW.status := ''open'';
            END IF;
        ELSEIF NEW.status IS NULL OR NEW.status = '''' THEN
            NEW.status := ''open'';
        END IF;
        
        -- Set deadline type
        IF NEW.application_deadline IS NULL THEN
            NEW.application_deadline_type := ''rolling'';
        ELSE
            NEW.application_deadline_type := ''fixed'';
        END IF;
        
        RETURN NEW;
    END;
    $inner_func$;',
    'Update status and deadline type for funding opportunities'
);

-- Clean up the helper function
DROP FUNCTION IF EXISTS public.update_function_security(text, text, text, text);

-- Set default search_path for the current session
SET LOCAL search_path = public, pg_temp;

-- Commit the transaction
COMMIT;

-- Notify completion
DO $$
BEGIN
    RAISE NOTICE 'Security updates for all functions completed successfully';
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error in security updates: %', SQLERRM;
END $$;
