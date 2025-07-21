-- Script to check the schema of africa_intelligence_feed
SELECT 
    column_name, 
    data_type,
    is_nullable,
    column_default,
    character_maximum_length
FROM 
    information_schema.columns 
WHERE 
    table_name = 'africa_intelligence_feed'
ORDER BY 
    ordinal_position;
