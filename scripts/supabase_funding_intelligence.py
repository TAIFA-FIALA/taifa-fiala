#!/usr/bin/env python3
"""
Apply Funding Intelligence Schema to Supabase using Supabase Client
Based on the Notion note: "Where to go from here? AI-Powered Funding Intelligence Pipeline"
"""

import os
import sys
from pathlib import Path
import logging
from supabase import create_client, Client
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('supabase_funding_intelligence.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SupabaseFundingIntelligence:
    """Handles the creation of funding intelligence schema in Supabase"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_API_KEY')  # Use service key for admin operations
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_API_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.schema_file = Path(__file__).parent.parent / "database" / "migrations" / "funding_intelligence_schema.sql"
    
    def create_tables_step_by_step(self):
        """Create tables step by step using individual SQL statements"""
        
        # Step 1: Create funding_signals table
        funding_signals_sql = """
        CREATE TABLE IF NOT EXISTS funding_signals (
            id SERIAL PRIMARY KEY,
            source_url VARCHAR(1000),
            source_type VARCHAR(50) NOT NULL,
            signal_type VARCHAR(50) NOT NULL,
            title VARCHAR(500),
            content TEXT NOT NULL,
            original_language VARCHAR(10) DEFAULT 'en',
            processed_content TEXT,
            
            -- AI Analysis Results
            funding_implications BOOLEAN DEFAULT FALSE,
            confidence_score FLOAT DEFAULT 0.0,
            funding_type VARCHAR(20),
            timeline VARCHAR(20),
            priority_score INTEGER DEFAULT 0,
            event_type VARCHAR(50),
            expected_funding_date DATE,
            estimated_amount VARCHAR(100),
            
            -- Extracted entities (JSON format)
            extracted_entities JSONB,
            relationships JSONB,
            predictions JSONB,
            suggested_actions JSONB,
            
            -- Analysis metadata
            ai_analysis_version VARCHAR(10) DEFAULT '1.0',
            analysis_rationale TEXT,
            key_insights TEXT,
            
            -- Investigation tracking
            investigation_status VARCHAR(20) DEFAULT 'pending',
            investigation_notes TEXT,
            follow_up_required BOOLEAN DEFAULT FALSE,
            follow_up_date DATE,
            
            -- Standard fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            processed_at TIMESTAMP,
            
            -- Constraints
            CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1),
            CONSTRAINT valid_priority CHECK (priority_score >= 0 AND priority_score <= 100)
        );
        """
        
        # Step 2: Create funding_entities table
        funding_entities_sql = """
        CREATE TABLE IF NOT EXISTS funding_entities (
            id SERIAL PRIMARY KEY,
            name VARCHAR(300) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            entity_subtype VARCHAR(50),
            
            -- Entity details
            aliases JSONB,
            description TEXT,
            website VARCHAR(500),
            location VARCHAR(200),
            sector VARCHAR(100),
            
            -- Funding capacity (for funders)
            estimated_funding_capacity NUMERIC(15,2),
            funding_focus_areas JSONB,
            typical_funding_range VARCHAR(100),
            
            -- Intelligence metadata
            confidence FLOAT DEFAULT 0.0,
            first_seen DATE DEFAULT CURRENT_DATE,
            last_seen DATE DEFAULT CURRENT_DATE,
            mention_count INTEGER DEFAULT 1,
            importance_score INTEGER DEFAULT 0,
            
            -- Attributes (flexible JSON storage)
            attributes JSONB,
            
            -- Verification status
            verification_status VARCHAR(20) DEFAULT 'unverified',
            verification_notes TEXT,
            
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            CONSTRAINT valid_entity_confidence CHECK (confidence >= 0 AND confidence <= 1),
            CONSTRAINT valid_importance CHECK (importance_score >= 0 AND importance_score <= 100)
        );
        """
        
        # Step 3: Create funding_relationships table
        funding_relationships_sql = """
        CREATE TABLE IF NOT EXISTS funding_relationships (
            id SERIAL PRIMARY KEY,
            source_entity_id INTEGER REFERENCES funding_entities(id),
            target_entity_id INTEGER REFERENCES funding_entities(id),
            source_entity_name VARCHAR(300),
            target_entity_name VARCHAR(300),
            
            -- Relationship details
            relationship_type VARCHAR(50) NOT NULL,
            confidence FLOAT DEFAULT 0.0,
            context TEXT,
            amount VARCHAR(100),
            
            -- Timeline
            relationship_date DATE,
            first_seen DATE DEFAULT CURRENT_DATE,
            last_seen DATE DEFAULT CURRENT_DATE,
            total_interactions INTEGER DEFAULT 1,
            
            -- Supporting evidence
            source_content TEXT,
            supporting_urls JSONB,
            evidence_strength VARCHAR(20) DEFAULT 'weak',
            
            -- Relationship status
            status VARCHAR(20) DEFAULT 'active',
            
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            CONSTRAINT valid_relationship_confidence CHECK (confidence >= 0 AND confidence <= 1),
            CONSTRAINT no_self_relationship CHECK (source_entity_id != target_entity_id)
        );
        """
        
        # Step 4: Create funding_predictions table
        funding_predictions_sql = """
        CREATE TABLE IF NOT EXISTS funding_predictions (
            id SERIAL PRIMARY KEY,
            signal_id INTEGER REFERENCES funding_signals(id),
            entity_id INTEGER REFERENCES funding_entities(id),
            
            -- Prediction details
            prediction_type VARCHAR(50) NOT NULL,
            predicted_opportunity TEXT NOT NULL,
            expected_date DATE,
            confidence FLOAT DEFAULT 0.0,
            rationale TEXT,
            
            -- Prediction metadata
            prediction_model_version VARCHAR(10) DEFAULT '1.0',
            prediction_factors JSONB,
            
            -- Tracking
            materialized BOOLEAN DEFAULT FALSE,
            materialized_date DATE,
            materialized_notes TEXT,
            accuracy_score FLOAT,
            
            -- Follow-up
            monitoring_status VARCHAR(20) DEFAULT 'active',
            next_review_date DATE,
            
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            CONSTRAINT valid_prediction_confidence CHECK (confidence >= 0 AND confidence <= 1),
            CONSTRAINT valid_accuracy CHECK (accuracy_score IS NULL OR (accuracy_score >= 0 AND accuracy_score <= 1))
        );
        """
        
        # Step 5: Create other tables
        other_tables = [
            """
            CREATE TABLE IF NOT EXISTS funding_timelines (
                id SERIAL PRIMARY KEY,
                entity_id INTEGER REFERENCES funding_entities(id),
                signal_id INTEGER REFERENCES funding_signals(id),
                
                event_date DATE NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_description TEXT,
                event_impact_score INTEGER DEFAULT 0,
                
                source_content TEXT,
                context JSONB,
                
                created_at TIMESTAMP DEFAULT NOW(),
                
                CONSTRAINT valid_impact_score CHECK (event_impact_score >= 0 AND event_impact_score <= 100)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS funding_patterns (
                id SERIAL PRIMARY KEY,
                pattern_name VARCHAR(100) NOT NULL,
                pattern_type VARCHAR(50) NOT NULL,
                
                description TEXT,
                pattern_data JSONB,
                confidence FLOAT DEFAULT 0.0,
                
                occurrence_count INTEGER DEFAULT 0,
                success_rate FLOAT DEFAULT 0.0,
                average_delay_days INTEGER,
                
                primary_entity_id INTEGER REFERENCES funding_entities(id),
                secondary_entity_id INTEGER REFERENCES funding_entities(id),
                
                first_observed DATE,
                last_observed DATE,
                pattern_status VARCHAR(20) DEFAULT 'active',
                
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                
                CONSTRAINT valid_pattern_confidence CHECK (confidence >= 0 AND confidence <= 1),
                CONSTRAINT valid_success_rate CHECK (success_rate >= 0 AND success_rate <= 1)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS success_stories (
                id SERIAL PRIMARY KEY,
                title VARCHAR(300) NOT NULL,
                description TEXT,
                
                recipient_entity_id INTEGER REFERENCES funding_entities(id),
                funder_entity_id INTEGER REFERENCES funding_entities(id),
                funding_amount VARCHAR(100),
                funding_date DATE,
                
                success_factors JSONB,
                key_lessons JSONB,
                replicable_elements JSONB,
                
                analyzed_by_ai BOOLEAN DEFAULT FALSE,
                ai_insights TEXT,
                similar_opportunities JSONB,
                
                source_url VARCHAR(1000),
                source_content TEXT,
                
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS event_intelligence (
                id SERIAL PRIMARY KEY,
                event_name VARCHAR(300) NOT NULL,
                event_type VARCHAR(50),
                event_date DATE,
                location VARCHAR(200),
                
                description TEXT,
                sponsors JSONB,
                speakers JSONB,
                themes JSONB,
                side_events JSONB,
                
                funding_announcements JSONB,
                potential_opportunities JSONB,
                decision_makers_present JSONB,
                
                funding_potential_score INTEGER DEFAULT 0,
                network_value_score INTEGER DEFAULT 0,
                
                monitored BOOLEAN DEFAULT FALSE,
                follow_up_required BOOLEAN DEFAULT FALSE,
                
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                
                CONSTRAINT valid_funding_potential CHECK (funding_potential_score >= 0 AND funding_potential_score <= 100),
                CONSTRAINT valid_network_value CHECK (network_value_score >= 0 AND network_value_score <= 100)
            );
            """
        ]
        
        # Execute all table creation statements
        tables = [
            ("funding_signals", funding_signals_sql),
            ("funding_entities", funding_entities_sql),
            ("funding_relationships", funding_relationships_sql),
            ("funding_predictions", funding_predictions_sql),
        ]
        
        for name, sql in tables:
            try:
                result = self.supabase.rpc('exec_sql', {'sql': sql}).execute()
                logger.info(f"✅ Created table: {name}")
                time.sleep(1)  # Small delay between operations
            except Exception as e:
                logger.error(f"❌ Failed to create table {name}: {e}")
                continue
        
        for i, sql in enumerate(other_tables):
            try:
                result = self.supabase.rpc('exec_sql', {'sql': sql}).execute()
                logger.info(f"✅ Created additional table {i+1}")
                time.sleep(1)
            except Exception as e:
                logger.error(f"❌ Failed to create additional table {i+1}: {e}")
                continue
    
    def create_indexes(self):
        """Create indexes for performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_funding_signals_type ON funding_signals(signal_type);",
            "CREATE INDEX IF NOT EXISTS idx_funding_signals_confidence ON funding_signals(confidence_score DESC);",
            "CREATE INDEX IF NOT EXISTS idx_funding_signals_priority ON funding_signals(priority_score DESC);",
            "CREATE INDEX IF NOT EXISTS idx_funding_signals_date ON funding_signals(created_at DESC);",
            "CREATE INDEX IF NOT EXISTS idx_funding_entities_type ON funding_entities(entity_type);",
            "CREATE INDEX IF NOT EXISTS idx_funding_entities_name ON funding_entities(name);",
            "CREATE INDEX IF NOT EXISTS idx_funding_relationships_source ON funding_relationships(source_entity_id);",
            "CREATE INDEX IF NOT EXISTS idx_funding_relationships_target ON funding_relationships(target_entity_id);",
            "CREATE INDEX IF NOT EXISTS idx_funding_predictions_entity ON funding_predictions(entity_id);",
        ]
        
        for index_sql in indexes:
            try:
                result = self.supabase.rpc('exec_sql', {'sql': index_sql}).execute()
                logger.info(f"✅ Created index")
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"❌ Failed to create index: {e}")
                continue
    
    def create_views(self):
        """Create views for common queries"""
        views = [
            """
            CREATE OR REPLACE VIEW high_priority_signals AS
            SELECT 
                id,
                signal_type,
                title,
                confidence_score,
                priority_score,
                funding_type,
                timeline,
                expected_funding_date,
                estimated_amount,
                created_at
            FROM funding_signals
            WHERE funding_implications = TRUE
              AND priority_score >= 70
              AND investigation_status = 'pending'
            ORDER BY priority_score DESC, confidence_score DESC;
            """,
            """
            CREATE OR REPLACE VIEW active_funding_relationships AS
            SELECT 
                fr.id,
                fr.source_entity_name,
                fr.target_entity_name,
                fr.relationship_type,
                fr.confidence,
                fr.amount,
                fr.relationship_date,
                se.entity_type as source_type,
                te.entity_type as target_type
            FROM funding_relationships fr
            LEFT JOIN funding_entities se ON fr.source_entity_id = se.id
            LEFT JOIN funding_entities te ON fr.target_entity_id = te.id
            WHERE fr.status = 'active'
              AND fr.confidence >= 0.5
            ORDER BY fr.confidence DESC, fr.relationship_date DESC;
            """,
            """
            CREATE OR REPLACE VIEW upcoming_opportunities AS
            SELECT 
                fp.id,
                fp.predicted_opportunity,
                fp.expected_date,
                fp.confidence,
                fp.rationale,
                fe.name as entity_name,
                fe.entity_type,
                fs.title as source_signal
            FROM funding_predictions fp
            LEFT JOIN funding_entities fe ON fp.entity_id = fe.id
            LEFT JOIN funding_signals fs ON fp.signal_id = fs.id
            WHERE fp.materialized = FALSE
              AND fp.monitoring_status = 'active'
              AND fp.expected_date >= CURRENT_DATE
            ORDER BY fp.expected_date ASC, fp.confidence DESC;
            """
        ]
        
        for view_sql in views:
            try:
                result = self.supabase.rpc('exec_sql', {'sql': view_sql}).execute()
                logger.info(f"✅ Created view")
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"❌ Failed to create view: {e}")
                continue
    
    def insert_seed_data(self):
        """Insert seed data"""
        try:
            # Insert seed entities
            seed_entities = [
                {
                    "name": "Google",
                    "entity_type": "funder",
                    "entity_subtype": "corporate",
                    "description": "Technology company with AI focus",
                    "website": "https://google.com",
                    "location": "Global",
                    "sector": "Technology",
                    "estimated_funding_capacity": 5000000000,
                    "funding_focus_areas": ["AI", "digital skills", "startup acceleration"],
                    "confidence": 1.0,
                    "importance_score": 90
                },
                {
                    "name": "Microsoft",
                    "entity_type": "funder",
                    "entity_subtype": "corporate",
                    "description": "Technology company with AI initiatives",
                    "website": "https://microsoft.com",
                    "location": "Global",
                    "sector": "Technology",
                    "estimated_funding_capacity": 3000000000,
                    "funding_focus_areas": ["AI for Good", "digital transformation", "skills development"],
                    "confidence": 1.0,
                    "importance_score": 90
                },
                {
                    "name": "World Bank",
                    "entity_type": "funder",
                    "entity_subtype": "multilateral",
                    "description": "International financial institution",
                    "website": "https://worldbank.org",
                    "location": "Global",
                    "sector": "Development",
                    "estimated_funding_capacity": 50000000000,
                    "funding_focus_areas": ["digital development", "AI", "education", "health"],
                    "confidence": 1.0,
                    "importance_score": 100
                }
            ]
            
            for entity in seed_entities:
                result = self.supabase.table('funding_entities').insert(entity).execute()
                logger.info(f"✅ Inserted entity: {entity['name']}")
                time.sleep(0.5)
            
            # Insert a test signal
            test_signal = {
                "source_type": "test",
                "signal_type": "partnership_announcement",
                "title": "AI-Powered Funding Intelligence Pipeline Launch",
                "content": "Implementation of comprehensive funding intelligence system based on Notion recommendations",
                "funding_implications": True,
                "confidence_score": 1.0,
                "funding_type": "direct",
                "timeline": "immediate",
                "priority_score": 100,
                "event_type": "system_launch",
                "analysis_rationale": "System implementation milestone",
                "key_insights": "New intelligence capabilities enabled"
            }
            
            result = self.supabase.table('funding_signals').insert(test_signal).execute()
            logger.info("✅ Inserted test signal")
            
        except Exception as e:
            logger.error(f"❌ Failed to insert seed data: {e}")
    
    def run_setup(self):
        """Run the complete setup process"""
        logger.info("🚀 Starting Funding Intelligence Setup for Supabase")
        
        try:
            # Create tables
            logger.info("📊 Creating tables...")
            self.create_tables_step_by_step()
            
            # Create indexes
            logger.info("🔍 Creating indexes...")
            self.create_indexes()
            
            # Create views
            logger.info("👁️ Creating views...")
            self.create_views()
            
            # Insert seed data
            logger.info("🌱 Inserting seed data...")
            self.insert_seed_data()
            
            logger.info("✅ Funding Intelligence Setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False


def main():
    """Main function"""
    print("🚀 Funding Intelligence Schema Setup for Supabase")
    print("=" * 60)
    
    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_API_KEY')
    
    if not supabase_url:
        print("❌ SUPABASE_URL environment variable not set")
        return 1
    
    if not supabase_key:
        print("❌ SUPABASE_API_KEY environment variable not set")
        print("   Please set your Supabase service key (not anon key)")
        return 1
    
    print(f"📍 Supabase URL: {supabase_url}")
    print(f"🔑 Service Key: {'*' * 20}...{supabase_key[-4:]}")
    
    # Ask for confirmation
    response = input("\n🤔 Proceed with setup? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Setup cancelled")
        return 1
    
    # Run setup
    setup = SupabaseFundingIntelligence()
    success = setup.run_setup()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Check your Supabase dashboard for the new tables")
        print("   2. Test the views and data")
        print("   3. Update your application code")
        print("   4. Run the funding intelligence pipeline")
        return 0
    else:
        print("\n❌ Setup failed!")
        print("   Check the log file: supabase_funding_intelligence.log")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)