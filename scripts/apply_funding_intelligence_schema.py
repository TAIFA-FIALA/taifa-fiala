#!/usr/bin/env python3
"""
Apply Funding Intelligence Schema to Supabase Database
Based on the Notion note: "Where to go from here? AI-Powered Funding Intelligence Pipeline"
"""

import asyncio
import os
import sys
from pathlib import Path
import logging

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.database import get_database
import asyncpg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('funding_intelligence_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FundingIntelligenceMigration:
    """Handles the migration of funding intelligence schema to Supabase"""
    
    def __init__(self):
        self.schema_file = Path(__file__).parent.parent / "database" / "migrations" / "funding_intelligence_schema.sql"
        self.db_config = {
            'host': settings.DATABASE_HOST,
            'database': settings.DATABASE_NAME,
            'user': settings.DATABASE_USER,
            'password': settings.DATABASE_PASSWORD,
            'port': settings.DATABASE_PORT,
        }
    
    async def connect_to_db(self):
        """Connect to the database"""
        try:
            self.connection = await asyncpg.connect(**self.db_config)
            logger.info("Successfully connected to database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    async def check_existing_tables(self):
        """Check which funding intelligence tables already exist"""
        tables_to_check = [
            'funding_signals',
            'funding_entities',
            'funding_relationships',
            'funding_predictions',
            'funding_timelines',
            'funding_patterns',
            'success_stories',
            'event_intelligence'
        ]
        
        existing_tables = []
        for table in tables_to_check:
            query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = $1
            );
            """
            result = await self.connection.fetchval(query, table)
            if result:
                existing_tables.append(table)
        
        return existing_tables
    
    async def backup_existing_tables(self, existing_tables):
        """Backup existing tables if they exist"""
        if not existing_tables:
            logger.info("No existing tables to backup")
            return
        
        logger.info(f"Backing up existing tables: {existing_tables}")
        
        for table in existing_tables:
            backup_table = f"{table}_backup_{int(asyncio.get_event_loop().time())}"
            query = f"CREATE TABLE {backup_table} AS SELECT * FROM {table};"
            
            try:
                await self.connection.execute(query)
                logger.info(f"Backed up {table} to {backup_table}")
            except Exception as e:
                logger.error(f"Failed to backup {table}: {e}")
    
    async def read_schema_file(self):
        """Read the schema file"""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schema_content = f.read()
            logger.info(f"Successfully read schema file: {self.schema_file}")
            return schema_content
        except Exception as e:
            logger.error(f"Failed to read schema file: {e}")
            return None
    
    async def execute_schema_migration(self, schema_content):
        """Execute the schema migration"""
        try:
            # Split the schema into individual statements
            statements = self._split_sql_statements(schema_content)
            
            # Execute each statement
            for i, statement in enumerate(statements):
                if statement.strip():
                    try:
                        await self.connection.execute(statement)
                        logger.info(f"Executed statement {i+1}/{len(statements)}")
                    except Exception as e:
                        logger.error(f"Failed to execute statement {i+1}: {e}")
                        logger.error(f"Statement: {statement[:100]}...")
                        # Continue with other statements
                        continue
            
            logger.info("Schema migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute schema migration: {e}")
            return False
    
    def _split_sql_statements(self, sql_content):
        """Split SQL content into individual statements"""
        # Remove comments
        lines = sql_content.split('\n')
        clean_lines = []
        
        for line in lines:
            # Remove line comments
            if '--' in line:
                line = line[:line.index('--')]
            clean_lines.append(line)
        
        clean_sql = '\n'.join(clean_lines)
        
        # Split by semicolons (simple approach)
        statements = []
        current_statement = ""
        
        for line in clean_sql.split('\n'):
            current_statement += line + '\n'
            
            # Check if this line ends a statement
            if line.strip().endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        # Add any remaining statement
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return [s for s in statements if s.strip() and not s.strip().startswith('--')]
    
    async def verify_migration(self):
        """Verify that the migration was successful"""
        try:
            # Check that all tables exist
            expected_tables = [
                'funding_signals',
                'funding_entities',
                'funding_relationships',
                'funding_predictions',
                'funding_timelines',
                'funding_patterns',
                'success_stories',
                'event_intelligence'
            ]
            
            existing_tables = await self.check_existing_tables()
            missing_tables = set(expected_tables) - set(existing_tables)
            
            if missing_tables:
                logger.error(f"Missing tables after migration: {missing_tables}")
                return False
            
            # Check that views exist
            views_to_check = [
                'high_priority_signals',
                'active_funding_relationships',
                'upcoming_opportunities',
                'recent_funding_activity'
            ]
            
            for view in views_to_check:
                query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.views 
                    WHERE table_schema = 'public' 
                    AND table_name = $1
                );
                """
                result = await self.connection.fetchval(query, view)
                if not result:
                    logger.warning(f"View {view} not found")
            
            # Test basic functionality
            test_queries = [
                "SELECT COUNT(*) FROM funding_signals",
                "SELECT COUNT(*) FROM funding_entities",
                "SELECT COUNT(*) FROM funding_relationships",
                "SELECT * FROM high_priority_signals LIMIT 1",
                "SELECT * FROM active_funding_relationships LIMIT 1"
            ]
            
            for query in test_queries:
                try:
                    await self.connection.fetchval(query)
                    logger.info(f"Test query successful: {query}")
                except Exception as e:
                    logger.error(f"Test query failed: {query} - {e}")
                    return False
            
            logger.info("Migration verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration verification failed: {e}")
            return False
    
    async def insert_seed_data(self):
        """Insert seed data for testing"""
        try:
            # Insert a test funding signal
            insert_signal = """
            INSERT INTO funding_signals (
                source_type, signal_type, title, content, funding_implications,
                confidence_score, funding_type, timeline, priority_score, event_type
            ) VALUES (
                'test', 'partnership_announcement', 'Test Funding Signal',
                'This is a test funding signal for the AI-Powered Funding Intelligence Pipeline',
                TRUE, 0.8, 'indirect', 'short_term', 75, 'partnership_announcement'
            ) ON CONFLICT DO NOTHING;
            """
            
            await self.connection.execute(insert_signal)
            logger.info("Inserted test funding signal")
            
            # Insert test entities if they don't exist
            test_entities = [
                ("Google", "funder", "corporate", "Technology company", "https://google.com"),
                ("Microsoft", "funder", "corporate", "Technology company", "https://microsoft.com"),
                ("Test Startup", "recipient", "startup", "AI startup in Africa", "https://teststartup.com")
            ]
            
            for name, entity_type, subtype, description, website in test_entities:
                insert_entity = """
                INSERT INTO funding_entities (
                    name, entity_type, entity_subtype, description, website, confidence
                ) VALUES ($1, $2, $3, $4, $5, 0.9)
                ON CONFLICT DO NOTHING;
                """
                await self.connection.execute(insert_entity, name, entity_type, subtype, description, website)
            
            logger.info("Inserted test entities")
            
            # Insert test relationship
            insert_relationship = """
            INSERT INTO funding_relationships (
                source_entity_name, target_entity_name, relationship_type, confidence, context
            ) VALUES (
                'Google', 'Test Startup', 'funds', 0.8, 'Test relationship for funding intelligence'
            ) ON CONFLICT DO NOTHING;
            """
            
            await self.connection.execute(insert_relationship)
            logger.info("Inserted test relationship")
            
            # Insert test prediction
            insert_prediction = """
            INSERT INTO funding_predictions (
                prediction_type, predicted_opportunity, expected_date, confidence, rationale
            ) VALUES (
                'funding_opportunity', 'Google AI for Africa Challenge', 
                CURRENT_DATE + INTERVAL '90 days', 0.7,
                'Based on partnership announcement patterns'
            ) ON CONFLICT DO NOTHING;
            """
            
            await self.connection.execute(insert_prediction)
            logger.info("Inserted test prediction")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert seed data: {e}")
            return False
    
    async def run_migration(self, backup_existing=True, insert_seed=True):
        """Run the complete migration process"""
        logger.info("Starting Funding Intelligence Schema Migration")
        
        # Connect to database
        if not await self.connect_to_db():
            return False
        
        try:
            # Check existing tables
            existing_tables = await self.check_existing_tables()
            logger.info(f"Found existing tables: {existing_tables}")
            
            # Backup existing tables if requested
            if backup_existing and existing_tables:
                await self.backup_existing_tables(existing_tables)
            
            # Read schema file
            schema_content = await self.read_schema_file()
            if not schema_content:
                return False
            
            # Execute migration
            if not await self.execute_schema_migration(schema_content):
                return False
            
            # Verify migration
            if not await self.verify_migration():
                return False
            
            # Insert seed data if requested
            if insert_seed:
                await self.insert_seed_data()
            
            logger.info("Funding Intelligence Schema Migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
        
        finally:
            if hasattr(self, 'connection'):
                await self.connection.close()
                logger.info("Database connection closed")


async def main():
    """Main function"""
    print("🚀 Funding Intelligence Schema Migration")
    print("=" * 50)
    
    # Check if schema file exists
    migration = FundingIntelligenceMigration()
    if not migration.schema_file.exists():
        print(f"❌ Schema file not found: {migration.schema_file}")
        return 1
    
    # Ask user for confirmation
    print(f"📁 Schema file: {migration.schema_file}")
    print(f"🗄️  Database: {settings.DATABASE_NAME}")
    
    response = input("\n🤔 Proceed with migration? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Migration cancelled")
        return 1
    
    # Run migration
    success = await migration.run_migration()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Review the migration log for any warnings")
        print("   2. Test the new tables and views")
        print("   3. Update your application code to use the new schema")
        print("   4. Run the funding intelligence pipeline")
        return 0
    else:
        print("\n❌ Migration failed!")
        print("   Check the log file for details: funding_intelligence_migration.log")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)