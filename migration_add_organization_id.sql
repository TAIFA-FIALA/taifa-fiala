-- Manual migration script to add organization_id foreign key
-- Run this script with: psql -f migration_add_organization_id.sql <your_database>

BEGIN;

-- Add organization_id column
ALTER TABLE funding_opportunities 
ADD COLUMN organization_id INTEGER;

-- Add foreign key constraint
ALTER TABLE funding_opportunities 
ADD CONSTRAINT fk_funding_opportunities_organization_id 
FOREIGN KEY (organization_id) REFERENCES organizations(id);

-- Add index for performance
CREATE INDEX idx_funding_opportunities_organization_id 
ON funding_opportunities(organization_id);

-- Add note about migration
INSERT INTO alembic_version (version_num) VALUES ('001') 
ON CONFLICT (version_num) DO NOTHING;

COMMIT;

-- Display completion message
\echo 'Migration completed successfully!'
\echo 'Column organization_id added to funding_opportunities table'
\echo 'Foreign key constraint and index created'
