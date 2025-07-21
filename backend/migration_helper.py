"""
Migration Helper for Supabase to SQLite Schema Synchronization

This module helps synchronize schema between Supabase (PostgreSQL) and local SQLite
for development and testing purposes.
"""
import os
import sys
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, MetaData, Table, Column, inspect
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.schema import CreateTable
import sqlalchemy as sa

# Add the app directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.core.config import settings
from app.core.base import Base
from app.models import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchemaConverter:
    """Convert PostgreSQL schema to SQLite-compatible schema"""
    
    TYPE_MAPPING = {
        # PostgreSQL -> SQLite type mappings
        'JSONB': sa.JSON,
        'JSON': sa.JSON,
        'UUID': lambda: sa.String(36),
        'ARRAY': sa.JSON,  # Convert arrays to JSON
        'BYTEA': sa.LargeBinary,
        'TEXT': sa.Text,
        'VARCHAR': sa.String,
        'INTEGER': sa.Integer,
        'BIGINT': sa.BigInteger,
        'SMALLINT': sa.SmallInteger,
        'BOOLEAN': sa.Boolean,
        'TIMESTAMP': sa.DateTime,
        'TIMESTAMPTZ': sa.DateTime,
        'DATE': sa.Date,
        'TIME': sa.Time,
        'DECIMAL': sa.Numeric,
        'NUMERIC': sa.Numeric,
        'REAL': sa.Float,
        'DOUBLE_PRECISION': sa.Float,
    }
    
    @classmethod
    def convert_column_type(cls, pg_type):
        """Convert PostgreSQL column type to SQLite-compatible type"""
        type_name = str(pg_type).upper()
        
        # Handle specific PostgreSQL types
        if isinstance(pg_type, postgresql.JSONB):
            return sa.JSON()
        elif isinstance(pg_type, postgresql.UUID):
            return sa.String(36)
        elif isinstance(pg_type, postgresql.ARRAY):
            return sa.JSON()
        elif 'ARRAY' in type_name:
            return sa.JSON()
        elif 'JSONB' in type_name:
            return sa.JSON()
        elif 'UUID' in type_name:
            return sa.String(36)
        
        # Return the original type if no conversion needed
        return pg_type
    
    @classmethod
    def convert_table_for_sqlite(cls, table: Table) -> Table:
        """Convert a PostgreSQL table definition to SQLite-compatible"""
        new_columns = []
        
        for column in table.columns:
            new_type = cls.convert_column_type(column.type)
            new_column = Column(
                column.name,
                new_type,
                primary_key=column.primary_key,
                nullable=column.nullable,
                default=column.default,
                autoincrement=column.autoincrement if hasattr(column, 'autoincrement') else None
            )
            new_columns.append(new_column)
        
        # Create new table with converted columns
        new_table = Table(
            table.name,
            MetaData(),
            *new_columns,
            schema=None  # SQLite doesn't support schemas
        )
        
        return new_table

class MigrationHelper:
    """Helper class for managing migrations between Supabase and SQLite"""
    
    def __init__(self):
        self.supabase_url = self._get_supabase_connection_url()
        self.sqlite_url = settings.DATABASE_URL if "sqlite" in settings.DATABASE_URL else "sqlite:///./test.db"
        self.converter = SchemaConverter()
        self.alembic_dir = os.path.join(current_dir, "alembic")
        self.versions_dir = os.path.join(self.alembic_dir, "versions")
    
    def _get_supabase_connection_url(self) -> Optional[str]:
        """Get Supabase connection URL for direct database access"""
        if all([settings.DB_USER, settings.DB_PASSWORD, settings.DB_HOST, settings.DB_PORT, settings.DB_NAME]):
            return f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        return None
    
    def get_local_schema(self) -> MetaData:
        """Get the local SQLAlchemy model schema"""
        return Base.metadata
    
    def get_supabase_schema(self) -> Optional[MetaData]:
        """Get the current Supabase database schema"""
        if not self.supabase_url:
            logger.warning("No Supabase connection URL available")
            return None
        
        try:
            engine = create_engine(self.supabase_url)
            metadata = MetaData()
            metadata.reflect(bind=engine)
            return metadata
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            return None
    
    def compare_schemas(self) -> Dict[str, Any]:
        """Compare local models with Supabase schema"""
        local_metadata = self.get_local_schema()
        supabase_metadata = self.get_supabase_schema()
        
        comparison = {
            'local_tables': set(local_metadata.tables.keys()),
            'supabase_tables': set(supabase_metadata.tables.keys()) if supabase_metadata else set(),
            'missing_in_supabase': set(),
            'missing_in_local': set(),
            'table_differences': {}
        }
        
        if supabase_metadata:
            comparison['missing_in_supabase'] = comparison['local_tables'] - comparison['supabase_tables']
            comparison['missing_in_local'] = comparison['supabase_tables'] - comparison['local_tables']
            
            # Compare common tables
            common_tables = comparison['local_tables'] & comparison['supabase_tables']
            for table_name in common_tables:
                local_table = local_metadata.tables[table_name]
                supabase_table = supabase_metadata.tables[table_name]
                
                local_columns = {col.name: col for col in local_table.columns}
                supabase_columns = {col.name: col for col in supabase_table.columns}
                
                comparison['table_differences'][table_name] = {
                    'missing_columns_in_supabase': set(local_columns.keys()) - set(supabase_columns.keys()),
                    'missing_columns_in_local': set(supabase_columns.keys()) - set(local_columns.keys()),
                    'type_differences': []
                }
        
        return comparison
    
    def generate_sqlite_schema(self) -> str:
        """Generate SQLite-compatible CREATE statements from local models"""
        local_metadata = self.get_local_schema()
        sqlite_engine = create_engine("sqlite:///:memory:")
        
        statements = []
        
        for table_name, table in local_metadata.tables.items():
            # Convert table for SQLite compatibility
            sqlite_table = self.converter.convert_table_for_sqlite(table)
            
            # Generate CREATE TABLE statement
            create_stmt = CreateTable(sqlite_table).compile(sqlite_engine)
            statements.append(str(create_stmt))
        
        return ";\n\n".join(statements) + ";"
    
    def create_sqlite_database(self, db_path: Optional[str] = None) -> bool:
        """Create SQLite database with converted schema"""
        if not db_path:
            db_path = self.sqlite_url.replace("sqlite:///", "")
        
        try:
            # Create SQLite engine
            sqlite_engine = create_engine(f"sqlite:///{db_path}")
            
            # Get local metadata and convert for SQLite
            local_metadata = self.get_local_schema()
            sqlite_metadata = MetaData()
            
            # Convert all tables
            for table_name, table in local_metadata.tables.items():
                sqlite_table = self.converter.convert_table_for_sqlite(table)
                sqlite_table.metadata = sqlite_metadata
            
            # Create all tables
            sqlite_metadata.create_all(sqlite_engine)
            
            logger.info(f"✅ SQLite database created successfully at {db_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create SQLite database: {e}")
            return False
    
    def sync_schema_to_sqlite(self) -> bool:
        """Synchronize current model schema to SQLite database"""
        try:
            # Create SQLite engine
            sqlite_engine = create_engine(self.sqlite_url)
            
            # Drop all existing tables
            metadata = MetaData()
            metadata.reflect(bind=sqlite_engine)
            metadata.drop_all(sqlite_engine)
            
            # Create new schema
            return self.create_sqlite_database()
            
        except Exception as e:
            logger.error(f"❌ Failed to sync schema to SQLite: {e}")
            return False
    
    def get_schema(self, source: str = "supabase") -> Optional[MetaData]:
        """
        Get schema from specified source (supabase or local)
        
        Args:
            source: Either 'supabase' to fetch from Supabase DB or 'local' for SQLAlchemy models
            
        Returns:
            MetaData object containing the schema
        """
        if source.lower() == "supabase":
            return self.get_supabase_schema()
        elif source.lower() == "local":
            return self.get_local_schema()
        else:
            logger.error(f"Invalid source '{source}'. Use 'supabase' or 'local'")
            return None
    
    def generate_migration_from_supabase(self, migration_name: str = None) -> bool:
        """
        Generate an Alembic migration based on current Supabase schema
        
        Args:
            migration_name: Optional name for the migration
            
        Returns:
            True if migration was generated successfully
        """
        if not migration_name:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            migration_name = f"sync_from_supabase_{timestamp}"
        
        try:
            # Get Supabase schema
            supabase_metadata = self.get_supabase_schema()
            if not supabase_metadata:
                logger.error("Could not fetch Supabase schema")
                return False
            
            # Generate migration file
            migration_content = self._generate_migration_content(
                supabase_metadata, 
                migration_name
            )
            
            # Write migration file
            migration_file = self._write_migration_file(migration_name, migration_content)
            
            logger.info(f"✅ Migration generated: {migration_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate migration: {e}")
            return False
    
    def _generate_migration_content(self, metadata: MetaData, migration_name: str) -> str:
        """Generate Alembic migration file content from metadata"""
        from datetime import datetime
        
        # Get next revision number
        revision_id = self._get_next_revision_id()
        
        # Generate table creation statements
        upgrade_ops = []
        downgrade_ops = []
        
        for table_name, table in metadata.tables.items():
            # Convert table for SQLite compatibility
            sqlite_table = self.converter.convert_table_for_sqlite(table)
            
            # Generate create table operation
            columns = []
            for col in sqlite_table.columns:
                col_def = f"sa.Column('{col.name}', {self._get_column_type_string(col.type)}"
                if col.primary_key:
                    col_def += ", primary_key=True"
                if not col.nullable:
                    col_def += ", nullable=False"
                if col.default is not None:
                    col_def += f", default={repr(col.default.arg) if hasattr(col.default, 'arg') else repr(col.default)}"
                col_def += ")"
                columns.append(col_def)
            
            upgrade_ops.append(f"""
    op.create_table('{table_name}',
        {',\n        '.join(columns)}
    )""")
            
            downgrade_ops.append(f"    op.drop_table('{table_name}')")
        
        # Generate foreign key constraints
        for table_name, table in metadata.tables.items():
            for fk in table.foreign_keys:
                upgrade_ops.append(f"""
    op.create_foreign_key(
        'fk_{table_name}_{fk.column.name}_{fk.column.table.name}',
        '{table_name}', '{fk.column.table.name}',
        ['{fk.parent.name}'], ['{fk.column.name}']
    )""")
        
        # Format the migration template without f-string issues
        upgrade_ops_str = ''.join(upgrade_ops)
        downgrade_ops_str = '\n'.join(reversed(downgrade_ops))
        latest_revision = self._get_latest_revision()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        migration_template = f'''"""
{migration_name}

Revision ID: {revision_id}
Revises: {latest_revision}
Create Date: {current_time}

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '{revision_id}'
down_revision = '{latest_revision}'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade database schema"""{upgrade_ops_str}

def downgrade() -> None:
    """Downgrade database schema"""
    {downgrade_ops_str}
'''
        
        return migration_template
    
    def _get_column_type_string(self, col_type) -> str:
        """Convert SQLAlchemy column type to string representation"""
        if isinstance(col_type, sa.JSON):
            return "sa.JSON()"
        elif isinstance(col_type, sa.String):
            if hasattr(col_type, 'length') and col_type.length:
                return f"sa.String({col_type.length})"
            return "sa.String()"
        elif isinstance(col_type, sa.Integer):
            return "sa.Integer()"
        elif isinstance(col_type, sa.Boolean):
            return "sa.Boolean()"
        elif isinstance(col_type, sa.DateTime):
            return "sa.DateTime()"
        elif isinstance(col_type, sa.Text):
            return "sa.Text()"
        else:
            return f"sa.{col_type.__class__.__name__}()"
    
    def _get_next_revision_id(self) -> str:
        """Generate next revision ID"""
        import uuid
        return str(uuid.uuid4())[:12]
    
    def _get_latest_revision(self) -> Optional[str]:
        """Get the latest revision ID from existing migrations"""
        try:
            import subprocess
            result = subprocess.run(
                ["alembic", "heads"], 
                cwd=current_dir,
                capture_output=True, 
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split()[0]
        except Exception:
            pass
        return None
    
    def _write_migration_file(self, migration_name: str, content: str) -> str:
        """Write migration content to file"""
        # Create versions directory if it doesn't exist
        os.makedirs(self.versions_dir, exist_ok=True)
        
        # Generate filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        revision_id = self._get_next_revision_id()
        filename = f"{timestamp}_{revision_id}_{migration_name}.py"
        filepath = os.path.join(self.versions_dir, filename)
        
        # Write file
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath
    
    def update_local_migration(self) -> bool:
        """
        Update local migration by fetching schema from Supabase
        This is the main function for keeping migrations up to date
        """
        logger.info("🔄 Updating local migration from Supabase schema...")
        
        # Compare schemas first
        comparison = self.compare_schemas()
        
        if not comparison['supabase_tables']:
            logger.error("❌ Cannot access Supabase schema")
            return False
        
        # Check if there are differences
        has_differences = (
            comparison['missing_in_local'] or 
            comparison['missing_in_supabase'] or
            any(any(diff.values()) for diff in comparison['table_differences'].values())
        )
        
        if not has_differences:
            logger.info("✅ Local models are already in sync with Supabase")
            return True
        
        # Generate migration from Supabase
        success = self.generate_migration_from_supabase("sync_with_supabase")
        
        if success:
            logger.info("✅ Migration generated successfully")
            logger.info("💡 Run 'alembic upgrade head' to apply the migration")
        
        return success
    
    def print_schema_comparison(self):
        """Print a detailed comparison of schemas"""
        comparison = self.compare_schemas()
        
        print("\n" + "="*60)
        print("SCHEMA COMPARISON REPORT")
        print("="*60)
        
        print(f"\nLocal Models: {len(comparison['local_tables'])} tables")
        for table in sorted(comparison['local_tables']):
            print(f"  - {table}")
        
        if comparison['supabase_tables']:
            print(f"\nSupabase Database: {len(comparison['supabase_tables'])} tables")
            for table in sorted(comparison['supabase_tables']):
                print(f"  - {table}")
        else:
            print("\nSupabase Database: Not accessible")
        
        if comparison['missing_in_supabase']:
            print(f"\n⚠️  Tables missing in Supabase:")
            for table in sorted(comparison['missing_in_supabase']):
                print(f"  - {table}")
        
        if comparison['missing_in_local']:
            print(f"\n⚠️  Tables missing in local models:")
            for table in sorted(comparison['missing_in_local']):
                print(f"  - {table}")
        
        if comparison['table_differences']:
            print(f"\n📊 Table differences:")
            for table_name, diffs in comparison['table_differences'].items():
                if any(diffs.values()):
                    print(f"\n  {table_name}:")
                    if diffs['missing_columns_in_supabase']:
                        print(f"    Missing in Supabase: {', '.join(diffs['missing_columns_in_supabase'])}")
                    if diffs['missing_columns_in_local']:
                        print(f"    Missing in local: {', '.join(diffs['missing_columns_in_local'])}")

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migration Helper for Supabase to SQLite")
    parser.add_argument("--compare", action="store_true", help="Compare schemas")
    parser.add_argument("--create-sqlite", action="store_true", help="Create SQLite database")
    parser.add_argument("--sync", action="store_true", help="Sync schema to SQLite")
    parser.add_argument("--generate-sql", action="store_true", help="Generate SQLite SQL")
    parser.add_argument("--get-schema", choices=["supabase", "local"], help="Get schema from source")
    parser.add_argument("--update-migration", action="store_true", help="Update local migration from Supabase")
    parser.add_argument("--generate-migration", help="Generate migration from Supabase with custom name")
    parser.add_argument("--db-path", help="SQLite database path")
    
    args = parser.parse_args()
    
    helper = MigrationHelper()
    
    if args.compare:
        helper.print_schema_comparison()
    
    if args.create_sqlite:
        helper.create_sqlite_database(args.db_path)
    
    if args.sync:
        helper.sync_schema_to_sqlite()
    
    if args.generate_sql:
        sql = helper.generate_sqlite_schema()
        print("\n" + "="*60)
        print("SQLITE SCHEMA SQL")
        print("="*60)
        print(sql)
    
    if args.get_schema:
        schema = helper.get_schema(args.get_schema)
        if schema:
            print(f"\n" + "="*60)
            print(f"{args.get_schema.upper()} SCHEMA")
            print("="*60)
            print(f"Tables: {len(schema.tables)}")
            for table_name in sorted(schema.tables.keys()):
                table = schema.tables[table_name]
                print(f"\n{table_name}:")
                for col in table.columns:
                    print(f"  - {col.name}: {col.type}")
    
    if args.update_migration:
        helper.update_local_migration()
    
    if args.generate_migration:
        helper.generate_migration_from_supabase(args.generate_migration)

if __name__ == "__main__":
    main()
