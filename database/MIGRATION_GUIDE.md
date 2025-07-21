# Enhanced Funding Schema Migration Guide

## Issue Resolution
The original migration failed because it tried to rename a column that already existed. The corrected migration script now accounts for the actual current schema structure.

## Manual Migration Steps

Since Supabase has limitations with complex SQL execution through the API, follow these steps to apply the migration manually:

### Step 1: Access Supabase SQL Editor
1. Open your Supabase Dashboard
2. Navigate to **SQL Editor**
3. Create a new query

### Step 2: Execute the Migration
1. Copy the contents of the migration file: `/database/migrations/enhanced_funding_schema_migration.sql`
2. Paste it into the SQL Editor
3. Click **Run** to execute the migration

### Step 3: Verify the Migration
Run these verification queries in the SQL Editor:

#### Check New Columns Added
```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'africa_intelligence_feed' 
AND column_name IN (
    'total_funding_pool', 
    'min_amount_per_project', 
    'max_amount_per_project', 
    'exact_amount_per_project',
    'target_audience', 
    'ai_subsectors',
    'gender_focused',
    'youth_focused',
    'collaboration_required',
    'urgency_level'
);
```

#### Check New Indexes Created
```sql
SELECT indexname 
FROM pg_indexes 
WHERE tablename = 'africa_intelligence_feed' 
AND (indexname LIKE '%enhanced%' OR 
     indexname LIKE '%target_audience%' OR 
     indexname LIKE '%ai_subsectors%' OR
     indexname LIKE '%funding_type%');
```

#### Check New Views Created
```sql
SELECT viewname 
FROM pg_views 
WHERE viewname IN ('funding_opportunities_by_type', 'urgent_funding_opportunities');
```

#### Check Data Migration Success
```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(CASE WHEN funding_type IS NOT NULL THEN 1 END) as records_with_funding_type,
    COUNT(CASE WHEN urgency_level IS NOT NULL THEN 1 END) as records_with_urgency,
    COUNT(CASE WHEN gender_focused IS NOT NULL THEN 1 END) as records_with_gender_focus
FROM africa_intelligence_feed;
```

### Step 4: Test the Enhanced Functionality

#### Test the Funding Type Classification
```sql
SELECT 
    funding_type,
    COUNT(*) as count,
    AVG(CASE 
        WHEN funding_type = 'total_pool' THEN total_funding_pool
        WHEN funding_type = 'per_project_exact' THEN exact_amount_per_project
        WHEN funding_type = 'per_project_range' THEN (min_amount_per_project + max_amount_per_project) / 2
    END) as avg_amount
FROM africa_intelligence_feed
WHERE funding_type IS NOT NULL
GROUP BY funding_type;
```

#### Test the Enhanced Views
```sql
-- Test funding opportunities by type view
SELECT * FROM funding_opportunities_by_type LIMIT 5;

-- Test urgent opportunities view  
SELECT * FROM urgent_funding_opportunities LIMIT 5;
```

#### Test Trigger Functionality
```sql
-- Insert a test record to verify triggers work
INSERT INTO africa_intelligence_feed (
    title, 
    description, 
    source_url, 
    application_deadline,
    target_audience
) VALUES (
    'Test Migration Record',
    'Testing the enhanced schema migration',
    'https://example.com/test',
    CURRENT_DATE + INTERVAL '15 days',
    '["startups", "researchers"]'::jsonb
);

-- Check if urgency was calculated automatically
SELECT 
    title, 
    urgency_level, 
    days_until_deadline, 
    is_deadline_approaching,
    suitable_for_startups,
    suitable_for_researchers
FROM africa_intelligence_feed 
WHERE title = 'Test Migration Record';

-- Clean up test record
DELETE FROM africa_intelligence_feed WHERE title = 'Test Migration Record';
```

## Expected Results

After successful migration, you should see:

### New Columns (at least 25+)
- **Funding Amount Fields**: `total_funding_pool`, `min_amount_per_project`, `max_amount_per_project`, `exact_amount_per_project`
- **Project Count Fields**: `estimated_project_count`, `project_count_range`
- **Process Fields**: `application_deadline_type`, `selection_criteria`, `project_duration`
- **Targeting Fields**: `target_audience`, `ai_subsectors`, `development_stage`
- **Focus Fields**: `gender_focused`, `youth_focused`, `collaboration_required`
- **Metadata Fields**: `urgency_level`, `days_until_deadline`, `is_deadline_approaching`

### New Indexes (10+)
- Performance indexes on all new amount fields
- GIN indexes on JSONB columns for fast querying
- Indexes on boolean flags for filtering

### New Views (2)
- `funding_opportunities_by_type`: Aggregated funding data by type
- `urgent_funding_opportunities`: Opportunities with approaching deadlines

### New Functions & Triggers (4+)
- `calculate_urgency_level()`: Automatic urgency calculation
- `update_urgency_fields()`: Trigger to update urgency on deadline changes
- `update_suitability_flags()`: Trigger to update suitability on audience changes

### Data Migration
- All existing records should have `funding_type` populated
- Records with deadlines should have `urgency_level` calculated
- Focus fields should be copied from existing `women_focus` and `youth_focus` columns

## Troubleshooting

### If Migration Fails
1. **Check Error Messages**: Look for specific column/constraint conflicts
2. **Run Parts Separately**: Execute the migration in smaller chunks
3. **Verify Prerequisites**: Ensure no conflicting constraints exist

### Common Issues
- **Column Already Exists**: The migration script handles this with `IF NOT EXISTS` checks
- **Constraint Conflicts**: Drop conflicting constraints before running migration
- **Permission Issues**: Ensure you have admin access to the database

### Rollback (if needed)
If you need to rollback the migration:

```sql
-- Remove new columns (WARNING: This will lose data)
ALTER TABLE africa_intelligence_feed 
DROP COLUMN IF EXISTS total_funding_pool,
DROP COLUMN IF EXISTS min_amount_per_project,
DROP COLUMN IF EXISTS max_amount_per_project,
-- ... (add other columns as needed)

-- Drop new views
DROP VIEW IF EXISTS funding_opportunities_by_type;
DROP VIEW IF EXISTS urgent_funding_opportunities;

-- Drop triggers
DROP TRIGGER IF EXISTS trigger_update_urgency_fields ON africa_intelligence_feed;
DROP TRIGGER IF EXISTS trigger_update_suitability_flags ON africa_intelligence_feed;
```

## Next Steps

After successful migration:

1. **Update ETL Pipeline**: Deploy the enhanced extraction patterns
2. **Update Frontend**: Deploy the enhanced UI components  
3. **Test Data Flow**: Verify new data is being captured correctly
4. **Monitor Performance**: Check query performance with new indexes
5. **Backfill Data**: Run enhanced extraction on existing records

## Support

If you encounter issues:
1. Check the migration logs for specific error messages
2. Verify the current schema matches expectations
3. Test individual components (views, triggers) separately
4. Consider running the enhanced testing script to validate functionality

The enhanced schema provides a solid foundation for tracking the three funding patterns and significantly improves data capture capabilities.
