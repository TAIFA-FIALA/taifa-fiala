-- Check the current security settings for the functions
SELECT 
    n.nspname as schema,
    p.proname as function_name,
    pg_get_function_arguments(p.oid) as arguments,
    l.lanname as language,
    p.prosecdef as security_definer,
    p.proconfig as search_path_config,
    pg_get_functiondef(p.oid) as function_definition
FROM 
    pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    JOIN pg_language l ON p.prolang = l.oid
WHERE 
    n.nspname = 'public'
    AND p.proname IN (
        'calculate_urgency_level',
        'update_urgency_fields',
        'update_suitability_flags',
        'update_funding_opportunity_status'
    )
ORDER BY 
    p.proname;
