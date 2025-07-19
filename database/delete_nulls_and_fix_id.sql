-- Delete records with NULL IDs and fix the ID column
-- This is the simplest approach

-- First, delete all records with NULL IDs
DELETE FROM africa_intelligence_feed WHERE id IS NULL;

-- Create a sequence if it doesn't exist
CREATE SEQUENCE IF NOT EXISTS africa_intelligence_feed_id_seq;

-- Set the sequence to start from the current max ID + 1
SELECT setval('africa_intelligence_feed_id_seq', COALESCE((SELECT MAX(id) FROM africa_intelligence_feed), 0) + 1, false);

-- Update the ID column to use the sequence as default and make it NOT NULL
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

-- Check record count after cleanup
SELECT COUNT(*) as total_records FROM africa_intelligence_feed;
