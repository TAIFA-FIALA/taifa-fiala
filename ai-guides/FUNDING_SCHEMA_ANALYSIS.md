# Funding Opportunities Schema Analysis and Fix

## Issue Summary
The data ingestion script was failing because it was trying to insert data with an `organization_name` column that doesn't exist in the `funding_opportunities` table.

## Root Cause
The script was using outdated field names that don't match the actual database schema.

## Database Schema Analysis

### Actual Columns in funding_opportunities Table:
- `id` (Primary Key)
- `title` (Required)
- `description` (Required)
- `source_url` (Required - NOT NULL)
- `application_url`
- `amount_min`, `amount_max`
- `application_deadline`
- `eligibility_criteria`
- `ai_domains`, `geographic_scopes`
- `funding_type_id`
- `provider_organization_id`, `recipient_organization_id`
- `grant_reporting_requirements`, `grant_duration_months`, `grant_renewable`
- `equity_percentage`, `valuation_cap`, `interest_rate`, `expected_roi`
- `status`
- `additional_resources`
- `equity_focus_details`
- `women_focus`, `underserved_focus`, `youth_focus`
- `created_at`, `updated_at`
- `funding_type`, `funding_amount`
- `application_process`, `contact_information`, `additional_notes`
- `source_type`, `collected_at`, `keywords`

### Key Differences from Script:
1. **Missing Column**: `organization_name` does not exist
2. **Organization References**: Use `provider_organization_id` and `recipient_organization_id` instead
3. **Required Fields**: `title`, `description`, and `source_url` are required

## Fix Applied

### Original Problematic Code:
```python
opportunity_data = {
    'title': title,
    'description': summary,
    'organization_name': feed.feed.get('title', 'Unknown'),  # ❌ Column doesn't exist
    'funding_type': 'opportunity',
    'application_deadline': None,
    'funding_amount': None,
    'eligibility_criteria': None,
    'application_process': None,
    'contact_information': entry.get('link', ''),
    'additional_notes': f'Collected from RSS feed: {feed_url}',
    'source_url': entry.get('link', ''),
    'source_type': 'rss',
    'keywords': '[]',
    'status': 'active'
}
```

### Fixed Code:
```python
opportunity_data = {
    'title': title,
    'description': summary,
    'source_url': entry.get('link', ''),  # ✅ Required field
    'application_url': entry.get('link', ''),
    'funding_type': 'opportunity',
    'application_deadline': None,
    'funding_amount': None,
    'eligibility_criteria': None,
    'application_process': None,
    'contact_information': entry.get('link', ''),
    'additional_notes': f'Collected from RSS feed: {feed_url}. Source: {feed.feed.get("title", "Unknown")}',  # ✅ Organization name moved to notes
    'source_type': 'rss',
    'keywords': '[]',
    'status': 'active'
}
```

## Changes Made:
1. **Removed** `organization_name` field (doesn't exist in schema)
2. **Added** `application_url` field
3. **Ensured** `source_url` is properly populated (required field)
4. **Moved** organization name information to `additional_notes` field
5. **Verified** all other fields match existing schema

## Test Results:
- ✅ Schema validation passed
- ✅ Data ingestion script runs successfully
- ✅ 35 items successfully ingested from RSS feeds
- ✅ All data correctly stored in database

## Recommendations:
1. **Update Documentation**: Ensure all ingestion scripts use the correct schema
2. **Add Validation**: Consider adding schema validation before insertion
3. **Organization Mapping**: If organization names are needed, create a mapping to `provider_organization_id`
4. **Field Mapping**: Create a field mapping reference for future development

## Files Modified:
- `/Users/drjforrest/dev/devprojects/ai-africa-funding-tracker/start_data_ingestion.py`

## Schema Reference Files:
- `/Users/drjforrest/dev/devprojects/ai-africa-funding-tracker/backend/supabase_migration_updated.sql` (Lines 204-317)
- `/Users/drjforrest/dev/devprojects/ai-africa-funding-tracker/discover_schema.py` (Testing utility)