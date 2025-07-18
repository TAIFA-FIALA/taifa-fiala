-- This script adds the missing foreign key constraint to the africa_intelligence_feed table.
-- This will allow PostgREST to correctly identify the relationship between africa_intelligence_feed and funding_types.

ALTER TABLE public.africa_intelligence_feed
ADD CONSTRAINT fk_africa_intelligence_feed_funding_type_id
FOREIGN KEY (funding_type_id)
REFERENCES public.funding_types (id)
ON DELETE SET NULL;

-- Optional: Add an index to the foreign key column for better performance.
CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_funding_type_id
ON public.africa_intelligence_feed (funding_type_id);