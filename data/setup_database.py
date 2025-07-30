#!/usr/bin/env python3
"""
TAIFA-FIALA Database Setup Script
Initialize SQLite database for n8n funding pipeline integration
"""

import sqlite3
import os
from pathlib import Path

def setup_database():
    """Initialize the SQLite database with schema and sample data"""
    
    # Database file path
    db_path = Path(__file__).parent / "taifa_fiala.db"
    sql_path = Path(__file__).parent / "init_database.sql"
    
    print(f"Setting up database at: {db_path}")
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read and execute SQL schema
        with open(sql_path, 'r') as f:
            sql_script = f.read()
        
        # Execute the schema
        cursor.executescript(sql_script)
        
        print("✅ Database schema created successfully")
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Created tables: {[table[0] for table in tables]}")
        
        # Insert sample funding opportunity for testing
        sample_opportunity = {
            'title': 'AI for Healthcare Innovation Grant',
            'description': 'Supporting AI-powered healthcare solutions for African communities',
            'organization': 'African Development Bank',
            'amount_exact': 150000,
            'currency': 'USD',
            'deadline': '2024-06-30',
            'location': 'Africa-wide',
            'sector': 'Healthcare',
            'stage': 'Early Stage',
            'eligibility': 'African startups and research institutions',
            'application_url': 'https://example.com/apply',
            'source_type': 'manual',
            'validation_status': 'approved',
            'relevance_score': 0.9,
            'is_active': 1,
            'is_open': 1
        }
        
        cursor.execute("""
            INSERT INTO funding_opportunities 
            (title, description, organization, amount_exact, currency, deadline, 
             location, sector, stage, eligibility, application_url, source_type, 
             validation_status, relevance_score, is_active, is_open)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sample_opportunity['title'],
            sample_opportunity['description'],
            sample_opportunity['organization'],
            sample_opportunity['amount_exact'],
            sample_opportunity['currency'],
            sample_opportunity['deadline'],
            sample_opportunity['location'],
            sample_opportunity['sector'],
            sample_opportunity['stage'],
            sample_opportunity['eligibility'],
            sample_opportunity['application_url'],
            sample_opportunity['source_type'],
            sample_opportunity['validation_status'],
            sample_opportunity['relevance_score'],
            sample_opportunity['is_active'],
            sample_opportunity['is_open']
        ))
        
        conn.commit()
        print("✅ Sample data inserted successfully")
        
        # Show database stats
        cursor.execute("SELECT COUNT(*) FROM funding_opportunities")
        count = cursor.fetchone()[0]
        print(f"📈 Total funding opportunities: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM organizations")
        org_count = cursor.fetchone()[0]
        print(f"🏢 Total organizations: {org_count}")
        
        cursor.execute("SELECT COUNT(*) FROM funding_sources")
        source_count = cursor.fetchone()[0]
        print(f"🔗 Total funding sources: {source_count}")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
    
    print(f"🎉 Database setup complete! Database file: {db_path}")
    return db_path

if __name__ == "__main__":
    setup_database()