-- Fix the ID column to be auto-incrementing primary key
-- This handles existing NULL values first

-- First, create a sequence if it doesn't exist
CREATE SEQUENCE IF NOT EXISTS africa_intelligence_feed_id_seq;

-- Find the current max non-null ID to set sequence start point
DO $$
DECLARE
    max_id INTEGER;
    next_id INTEGER := 1;
BEGIN
    -- Get the maximum existing non-null ID
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM africa_intelligence_feed WHERE id IS NOT NULL;
    next_id := max_id + 1;
    
    -- Set the sequence to start from max_id + 1
    PERFORM setval('africa_intelligence_feed_id_seq', next_id, false);
    
    -- Update all NULL id values with sequential IDs
    UPDATE africa_intelligence_feed 
    SET id = nextval('africa_intelligence_feed_id_seq')
    WHERE id IS NULL;
END $$;

-- Now update the ID column to use the sequence as default and make it NOT NULL
ALTER TABLE africa_intelligence_feed 
ALTER COLUMN id SET DEFAULT nextval('africa_intelligence_feed_id_seq'),
ALTER COLUMN id SET NOT NULL;

-- Set the sequence to be owned by the column (for proper cleanup)
ALTER SEQUENCE africa_intelligence_feed_id_seq OWNED BY africa_intelligence_feed.id;

-- Add primary key constraint if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'africa_intelligence_feed' 
        AND constraint_type = 'PRIMARY KEY'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD PRIMARY KEY (id);
    END IF;
END $$;

-- Refresh PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- Verify the fix
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'africa_intelligence_feed' 
  AND column_name = 'id';

-- Also check that no NULL IDs remain
SELECT COUNT(*) as null_id_count FROM africa_intelligence_feed WHERE id IS NULL;
