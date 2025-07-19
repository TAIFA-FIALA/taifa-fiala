-- Add missing fields to africa_intelligence_feed table
-- Run this in your Supabase SQL editor

-- Check if currency column exists and add if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'currency'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN currency VARCHAR(10) DEFAULT 'USD';
        CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_currency ON africa_intelligence_feed(currency);
    END IF;
END $$;

-- Check if amount_exact column exists and add if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'amount_exact'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN amount_exact FLOAT;
    END IF;
END $$;

-- Check if type_id column exists and add if missing (this should be the foreign key to funding_types)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'type_id'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN type_id INTEGER REFERENCES funding_types(id);
        CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_type_id ON africa_intelligence_feed(type_id);
    END IF;
END $$;

-- Ensure funding_type_id column exists for backward compatibility
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'africa_intelligence_feed' 
        AND column_name = 'funding_type_id'
    ) THEN
        ALTER TABLE africa_intelligence_feed ADD COLUMN funding_type_id INTEGER REFERENCES funding_types(id);
        CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_funding_type_id ON africa_intelligence_feed(funding_type_id);
    END IF;
END $$;

-- Refresh PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- Verify the columns exist
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'africa_intelligence_feed' 
AND column_name IN ('currency', 'amount_exact', 'type_id', 'funding_type_id', 'amount_min', 'amount_max')
ORDER BY column_name;
