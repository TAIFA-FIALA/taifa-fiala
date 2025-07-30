#!/usr/bin/env python3
"""
Quick fix script for migration_helper.py f-string syntax error
This can be run directly on the production server to fix the issue
"""

import os
import re

def fix_migration_helper():
    """Fix the f-string syntax error in migration_helper.py"""
    
    # Path to the migration helper file
    file_path = "/Users/jforrest/production/taifa-fiala/backend/migration_helper.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find and fix the problematic f-string
        old_pattern = r'''migration_template = f\'\'\'\"""
\{migration_name\}

Revision ID: \{revision_id\}
Revises: \{self\._get_latest_revision\(\)\}
Create Date: \{datetime\.now\(\)\.strftime\("%Y-%m-%d %H:%M:%S\.%f"\)\}

\"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy\.dialects import sqlite

# revision identifiers, used by Alembic\.
revision = '\{revision_id\}'
down_revision = '\{self\._get_latest_revision\(\)\}'
branch_labels = None
depends_on = None

def upgrade\(\) -> None:
    \"""Upgrade database schema\"""\{\'\'\.join\(upgrade_ops\)\}

def downgrade\(\) -> None:
    \"""Downgrade database schema\"""
\{\'\'\.join\(reversed\(downgrade_ops\)\)\}
\'\'\''''

        new_content = '''# Format the migration template without f-string issues
        upgrade_ops_str = ''.join(upgrade_ops)
        downgrade_ops_str = '\\n'.join(reversed(downgrade_ops))
        latest_revision = self._get_latest_revision()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        migration_template = f\'\'\'\"""
{migration_name}

Revision ID: {revision_id}
Revises: {latest_revision}
Create Date: {current_time}

\"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '{revision_id}'
down_revision = '{latest_revision}'
branch_labels = None
depends_on = None

def upgrade() -> None:
    \"""Upgrade database schema\"""{upgrade_ops_str}

def downgrade() -> None:
    \"""Downgrade database schema\"""
    {downgrade_ops_str}
\'\'\''''

        # Replace the problematic section
        if "{''.join(upgrade_ops)}" in content and "{''.join(reversed(downgrade_ops))}" in content:
            # Find the start of the problematic function
            start_marker = "def _generate_migration_content(self, metadata: MetaData, migration_name: str) -> str:"
            end_marker = "return migration_template"
            
            start_idx = content.find(start_marker)
            if start_idx == -1:
                print("❌ Could not find _generate_migration_content function")
                return False
            
            # Find the end of the function
            end_idx = content.find(end_marker, start_idx)
            if end_idx == -1:
                print("❌ Could not find end of _generate_migration_content function")
                return False
            
            end_idx = content.find('\n', end_idx) + 1  # Include the return statement line
            
            # Extract the function content that needs fixing
            function_content = content[start_idx:end_idx]
            
            # Replace the problematic f-string section
            fixed_function = function_content.replace(
                "        migration_template = f'''\"\"\"",
                "        # Format the migration template without f-string issues\n"
                "        upgrade_ops_str = ''.join(upgrade_ops)\n"
                "        downgrade_ops_str = '\\n'.join(reversed(downgrade_ops))\n"
                "        latest_revision = self._get_latest_revision()\n"
                "        current_time = datetime.now().strftime(\"%Y-%m-%d %H:%M:%S.%f\")\n"
                "        \n"
                "        migration_template = f'''\"\"\"",
            ).replace(
                "{''.join(upgrade_ops)}",
                "{upgrade_ops_str}"
            ).replace(
                "{''.join(reversed(downgrade_ops))}",
                "{downgrade_ops_str}"
            ).replace(
                "{self._get_latest_revision()}",
                "{latest_revision}"
            ).replace(
                "{datetime.now().strftime(\"%Y-%m-%d %H:%M:%S.%f\")}",
                "{current_time}"
            )
            
            # Replace in the full content
            new_full_content = content[:start_idx] + fixed_function + content[end_idx:]
            
            # Write the fixed content back
            with open(file_path, 'w') as f:
                f.write(new_full_content)
            
            print("✅ Fixed migration_helper.py f-string syntax error")
            return True
        else:
            print("✅ File appears to already be fixed")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing file: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing migration_helper.py syntax error...")
    success = fix_migration_helper()
    if success:
        print("✅ Fix completed successfully")
    else:
        print("❌ Fix failed")
