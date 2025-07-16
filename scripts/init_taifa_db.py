#!/usr/bin/env python3
"""
Initialize TAIFA_db with tables and sample data
"""

from sqlalchemy import create_engine, text
from datetime import datetime
import sys

# Direct database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

def create_tables():
    """Create all necessary tables"""
    print("🏗️  Creating database tables...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Organizations table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS organizations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(300) NOT NULL,
                    type VARCHAR(20) DEFAULT 'funder',
                    country VARCHAR(100),
                    region VARCHAR(100),
                    website VARCHAR(500),
                    email VARCHAR(200),
                    description TEXT,
                    funding_capacity VARCHAR(50),
                    focus_areas TEXT,
                    established_year INTEGER,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                );
            """))
            
            # AI Domains table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ai_domains (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL UNIQUE,
                    description TEXT,
                    parent_id INTEGER REFERENCES ai_domains(id)
                );
            """))
            
            # Funding Categories table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS funding_categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL UNIQUE,
                    description TEXT,
                    parent_id INTEGER REFERENCES funding_categories(id)
                );
            """))
            
            # Data Sources table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS data_sources (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(300) NOT NULL,
                    url VARCHAR(1000) NOT NULL,
                    type VARCHAR(20) DEFAULT 'rss',
                    check_interval_minutes INTEGER DEFAULT 60,
                    last_checked TIMESTAMP WITH TIME ZONE,
                    last_successful_check TIMESTAMP WITH TIME ZONE,
                    reliability_score NUMERIC(3,2) DEFAULT 1.0,
                    total_opportunities_found INTEGER DEFAULT 0,
                    successful_checks INTEGER DEFAULT 0,
                    failed_checks INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT true,
                    status_message TEXT,
                    parser_config TEXT,
                    classification_keywords TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                );
            """))
            
            # Funding Opportunities table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS funding_opportunities (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    amount NUMERIC(15, 2),
                    currency VARCHAR(3) DEFAULT 'USD',
                    amount_usd NUMERIC(15, 2),
                    deadline TIMESTAMP WITH TIME ZONE,
                    announcement_date TIMESTAMP WITH TIME ZONE,
                    start_date TIMESTAMP WITH TIME ZONE,
                    status VARCHAR(20) DEFAULT 'active',
                    source_url VARCHAR(1000),
                    contact_info TEXT,
                    geographical_scope TEXT,
                    eligibility_criteria TEXT,
                    application_deadline TIMESTAMP WITH TIME ZONE,
                    max_funding_period_months INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE,
                    last_checked TIMESTAMP WITH TIME ZONE,
                    source_organization_id INTEGER REFERENCES organizations(id),
                    data_source_id INTEGER REFERENCES data_sources(id)
                );
            """))
            
            # Association tables for many-to-many relationships
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS funding_ai_domains (
                    funding_id INTEGER REFERENCES funding_opportunities(id),
                    ai_domain_id INTEGER REFERENCES ai_domains(id),
                    PRIMARY KEY (funding_id, ai_domain_id)
                );
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS funding_categories_rel (
                    funding_id INTEGER REFERENCES funding_opportunities(id),
                    category_id INTEGER REFERENCES funding_categories(id),
                    PRIMARY KEY (funding_id, category_id)
                );
            """))
            
            conn.commit()
            print("✅ All tables created successfully!")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def load_sample_data():
    """Load sample data"""
    print("📊 Loading sample data...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Insert sample organizations
            conn.execute(text("""
                INSERT INTO organizations (name, type, country, region, website, description, funding_capacity, focus_areas)
                SELECT * FROM (VALUES 
                ('Bill & Melinda Gates Foundation', 'funder', 'United States', 'Global', 'https://www.gatesfoundation.org', 'Global foundation focused on health, development, and education', 'Large', '["Health", "Development", "AI for Good"]'),
                ('Science for Africa Foundation', 'funder', 'Kenya', 'East Africa', 'https://scienceforafrica.foundation', 'Supporting African-led scientific innovation', 'Medium', '["Science", "Innovation", "AI Research"]'),
                ('IDRC (International Development Research Centre)', 'funder', 'Canada', 'Global', 'https://idrc-crdi.ca', 'Canadian crown corporation supporting research in developing countries', 'Large', '["Development", "Research", "AI4D"]')
                ) AS t(name, type, country, region, website, description, funding_capacity, focus_areas)
                WHERE NOT EXISTS (SELECT 1 FROM organizations WHERE organizations.name = t.name);
            """))
            
            # Insert sample AI domains
            conn.execute(text("""
                INSERT INTO ai_domains (name, description)
                SELECT * FROM (VALUES 
                ('Healthcare AI', 'AI applications in healthcare and medical research'),
                ('Agricultural AI', 'AI for agriculture and food security'),
                ('Education AI', 'AI in education and learning'),
                ('Governance AI', 'AI for governance and public services'),
                ('Financial AI', 'AI for financial inclusion and fintech')
                ) AS t(name, description)
                WHERE NOT EXISTS (SELECT 1 FROM ai_domains WHERE ai_domains.name = t.name);
            """))
            
            # Insert sample funding categories
            conn.execute(text("""
                INSERT INTO funding_categories (name, description)
                SELECT * FROM (VALUES 
                ('Research Grants', 'Funding for research projects'),
                ('Implementation Funding', 'Funding for deploying AI solutions'),
                ('Capacity Building', 'Training and education funding'),
                ('Innovation Prizes', 'Competition-based funding'),
                ('Scholarships', 'Individual researcher support')
                ) AS t(name, description)
                WHERE NOT EXISTS (SELECT 1 FROM funding_categories WHERE funding_categories.name = t.name);
            """))
            
            # Insert sample data sources
            conn.execute(text("""
                INSERT INTO data_sources (name, url, type, classification_keywords)
                SELECT * FROM (VALUES 
                ('IDRC AI4D Program', 'https://idrc-crdi.ca/en/funding/funding-opportunities/rss', 'rss', 'AI,artificial intelligence,AI4D,machine learning'),
                ('Science for Africa Foundation', 'https://scienceforafrica.foundation/feed/', 'rss', 'AI,artificial intelligence,grand challenges,innovation'),
                ('Gates Foundation', 'https://www.gatesfoundation.org/ideas/rss/', 'rss', 'AI,artificial intelligence,health,development')
                ) AS t(name, url, type, classification_keywords)
                WHERE NOT EXISTS (SELECT 1 FROM data_sources WHERE data_sources.name = t.name);
            """))
            
            # Insert a sample funding opportunity
            conn.execute(text("""
                INSERT INTO funding_opportunities (
                    title, description, amount, currency, amount_usd, status, 
                    source_url, geographical_scope, eligibility_criteria, source_organization_id
                )
                SELECT * FROM (VALUES (
                    'AI for Health Innovation Grant', 
                    'Supporting AI innovations to improve healthcare outcomes in Africa. This grant supports researchers and organizations developing AI solutions for health challenges across the continent.',
                    100000, 'USD', 100000, 'active',
                    'https://example.com/ai-health-grant',
                    'Sub-Saharan Africa',
                    'African organizations, universities, and researchers',
                    1
                )) AS t(title, description, amount, currency, amount_usd, status, source_url, geographical_scope, eligibility_criteria, source_organization_id)
                WHERE NOT EXISTS (SELECT 1 FROM funding_opportunities WHERE funding_opportunities.title = t.title);
            """))
            
            conn.commit()
            print("✅ Sample data loaded successfully!")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return False

def main():
    """Main initialization function"""
    print("🚀 Initializing TAIFA_db - Tracking AI Funding for Africa")
    print("=" * 60)
    
    # Create tables
    print("\n1. Creating database tables...")
    if not create_tables():
        return False
    
    # Load sample data
    print("\n2. Loading sample data...")
    if not load_sample_data():
        return False
    
    print("\n🎉 Database initialization completed successfully!")
    print(f"\nTAIFA_db is ready on mac-mini!")
    print("\nNext steps:")
    print("1. Start the backend: cd backend && uvicorn app.main:app --reload")
    print("2. Start the Streamlit app: cd frontend/streamlit_app && streamlit run app.py")
    print("3. Visit http://localhost:8000/docs for API documentation")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
