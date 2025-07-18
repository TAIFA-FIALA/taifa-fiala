#!/usr/bin/env python3
"""
Update Code References Migration
===============================

This script updates all code references from 'africa_intelligence_feed' 
to 'africa_intelligence_feed' across the entire codebase.
"""

import os
import re
from pathlib import Path

# Define the replacement mappings
REPLACEMENTS = {
    'africa_intelligence_feed': 'africa_intelligence_feed',
    'AfricaIntelligenceItem': 'AfricaIntelligenceItem',
    'intelligence_item': 'intelligence_item',
    'AfricaIntelligenceFeed': 'AfricaIntelligenceFeed',
    'intelligenceItem': 'intelligenceItem',
    'intelligenceFeed': 'intelligenceFeed',
    'AFRICA_INTELLIGENCE_FEED': 'AFRICA_INTELLIGENCE_FEED',
    'Intelligence Item': 'Intelligence Item',
    'intelligence item': 'intelligence item',
    'Intelligence Feed': 'Intelligence Feed',
    'intelligence feed': 'intelligence feed'
}

def update_file_content(file_path):
    """Update content in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply replacements
        for old_text, new_text in REPLACEMENTS.items():
            content = content.replace(old_text, new_text)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def find_and_update_files():
    """Find and update all relevant files"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # File extensions to search
    extensions = ['.py', '.sql', '.md', '.txt', '.json', '.yaml', '.yml', '.js', '.ts', '.html']
    
    # Directories to exclude
    exclude_dirs = ['venv', '.git', '__pycache__', 'node_modules', '.pytest_cache']
    
    updated_files = []
    
    for file_path in project_root.rglob('*'):
        # Skip directories and excluded paths
        if file_path.is_dir():
            continue
        
        if any(exclude_dir in str(file_path) for exclude_dir in exclude_dirs):
            continue
        
        # Check if file has relevant extension
        if file_path.suffix in extensions:
            if update_file_content(file_path):
                updated_files.append(str(file_path))
    
    return updated_files

def update_dashboard_references():
    """Update specific dashboard references"""
    
    # Update system_dashboard.py
    dashboard_file = Path(__file__).parent / 'system_dashboard.py'
    
    if dashboard_file.exists():
        with open(dashboard_file, 'r') as f:
            content = f.read()
        
        # Update table references
        content = content.replace(
            "self.supabase.table('africa_intelligence_feed')",
            "self.supabase.table('africa_intelligence_feed')"
        )
        
        # Update display text
        content = content.replace(
            "intelligence feed",
            "intelligence items"
        )
        
        content = content.replace(
            "Intelligence Feed",
            "Intelligence Feed"
        )
        
        with open(dashboard_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated dashboard references")

def update_ingestion_scripts():
    """Update ingestion script references"""
    
    scripts = [
        'start_data_ingestion.py',
        'enhanced_data_ingestion.py',
        'scraping_queue_processor.py',
        'intelligent_serper_system.py',
        'pinecone_search_demo.py'
    ]
    
    project_root = Path(__file__).parent
    
    for script_name in scripts:
        script_path = project_root / script_name
        
        if script_path.exists():
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Update table references
            content = content.replace(
                "table('africa_intelligence_feed')",
                "table('africa_intelligence_feed')"
            )
            
            # Update variable names
            content = content.replace('africa_intelligence_feed', 'intelligence_feed')
            content = content.replace('opportunity_data', 'intelligence_data')
            content = content.replace('opportunities', 'intelligence_items')
            
            with open(script_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Updated {script_name}")

def create_summary_report():
    """Create a summary of changes made"""
    
    summary = """
# Table Rename Summary Report

## Changes Made:

### 1. Table Rename
- **Old**: `africa_intelligence_feed`
- **New**: `africa_intelligence_feed`

### 2. Content Classification
- Added content categories: funding, technology, policy, health, education, climate, economy, general
- Added geographic focus extraction
- Added relevance scoring
- Added AI extraction flags

### 3. Backward Compatibility
- Created view `africa_intelligence_feed` for backward compatibility
- View only shows items with content_category = 'funding'

### 4. Code Updates
- Updated all Python scripts to use new table name
- Updated dashboard references
- Updated ingestion scripts
- Updated search and scraping systems

### 5. New Features
- Better content categorization
- Geographic focus detection
- Sector tagging capability
- Relevance scoring

## Benefits:

1. **Accurate Naming**: Table name now reflects actual content
2. **Better Organization**: Content properly categorized
3. **Enhanced Search**: Geographic and sector filtering
4. **Improved Analytics**: Better metrics and reporting
5. **Backward Compatibility**: Existing code still works

## Next Steps:

1. Run the migration script in Supabase SQL Editor
2. Test all systems with new table structure
3. Update any remaining references
4. Monitor system performance
"""
    
    with open('TABLE_RENAME_SUMMARY.md', 'w') as f:
        f.write(summary)
    
    print("✅ Created summary report: TABLE_RENAME_SUMMARY.md")

def main():
    """Main function"""
    print("🚀 Starting code references update...")
    
    # Update specific files
    update_dashboard_references()
    update_ingestion_scripts()
    
    # Find and update all files
    updated_files = find_and_update_files()
    
    print(f"\n📊 Summary:")
    print(f"✅ Updated {len(updated_files)} files")
    
    if updated_files:
        print("\n📝 Updated files:")
        for file_path in updated_files:
            print(f"  - {file_path}")
    
    # Create summary report
    create_summary_report()
    
    print("\n🎉 Code references update completed!")
    print("\nNext steps:")
    print("1. Run the SQL migration: rename_table_migration.sql")
    print("2. Test the updated systems")
    print("3. Update any remaining references")

if __name__ == "__main__":
    main()