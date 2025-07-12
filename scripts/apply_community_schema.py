#!/usr/bin/env python3
"""
Apply community database schema to TAIFA-FIALA database
Adds community features for user engagement and collaboration
"""

import asyncio
import logging
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_collectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def apply_community_schema():
    """Apply the community database schema"""
    try:
        from database.connector import DatabaseConnector
        
        logger.info("🏗️ Applying TAIFA-FIALA community database schema...")
        
        # Initialize database connector
        db = DatabaseConnector()
        await db.initialize()
        
        # Read the community schema from the Python file
        from community_database_schema import community_schema_sql
        
        # Execute the schema
        async with db.pool.acquire() as conn:
            await conn.execute(community_schema_sql)
        
        logger.info("✅ Community schema applied successfully!")
        
        # Test the new community tables
        logger.info("🧪 Testing new community tables...")
        
        async with db.pool.acquire() as conn:
            # Check community badges
            badges = await conn.fetch("SELECT name, description, icon FROM community_badges ORDER BY name")
            logger.info(f"📊 Community badges: {len(badges)}")
            for badge in badges:
                logger.info(f"   {badge['icon']} {badge['name']}: {badge['description']}")
            
            # Check regional chapters
            chapters = await conn.fetch("SELECT name, description FROM regional_chapters ORDER BY name")
            logger.info(f"🌍 Regional chapters: {len(chapters)}")
            for chapter in chapters:
                logger.info(f"   📍 {chapter['name']}: {chapter['description']}")
            
            # Check community health metrics view
            health_check = await conn.fetchrow("SELECT * FROM community_health_metrics")
            logger.info(f"📈 Community health metrics initialized:")
            logger.info(f"   Active users: {health_check['active_users']}")
            logger.info(f"   Countries represented: {health_check['countries_represented']}")
            logger.info(f"   Published stories: {health_check['published_stories']}")
        
        await db.close()
        
        logger.info("🎉 TAIFA-FIALA community infrastructure is ready!")
        logger.info("")
        logger.info("📋 Next Steps:")
        logger.info("1. Implement user registration system in FastAPI")
        logger.info("2. Create community submission forms in Streamlit")
        logger.info("3. Build peer review workflow")
        logger.info("4. Set up regional ambassador program")
        logger.info("5. Launch beta testing with 20-30 community leaders")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Community schema application failed: {e}")
        return False

async def create_test_community_data():
    """Create some test community data for development"""
    try:
        from database.connector import DatabaseConnector
        
        logger.info("🧪 Creating test community data...")
        
        db = DatabaseConnector()
        await db.initialize()
        
        async with db.pool.acquire() as conn:
            # Create test users
            test_users = [
                {
                    'email': 'jamie@taifa-fiala.net',
                    'username': 'jamie_founder',
                    'full_name': 'Jamie Forrest',
                    'role': 'admin',
                    'country': 'Canada',
                    'organization': 'TAIFA-FIALA',
                    'expertise_areas': ['AI research', 'funding', 'platform development'],
                    'bio': 'Founder of TAIFA-FIALA, supporting AI development across Africa'
                },
                {
                    'email': 'test.researcher@university.edu',
                    'username': 'ai_researcher_001',
                    'full_name': 'Dr. Amina Hassan',
                    'role': 'contributor',
                    'country': 'Nigeria',
                    'organization': 'University of Lagos',
                    'expertise_areas': ['health AI', 'machine learning', 'research'],
                    'bio': 'AI researcher focusing on healthcare applications in Africa'
                },
                {
                    'email': 'startup.founder@tech.com',
                    'username': 'kwame_startup',
                    'full_name': 'Kwame Asante',
                    'role': 'contributor',
                    'country': 'Ghana',
                    'organization': 'AgTech Innovations',
                    'expertise_areas': ['agriculture AI', 'startups', 'implementation'],
                    'bio': 'Founder of AI-powered agricultural solutions for smallholder farmers'
                }
            ]
            
            for user_data in test_users:
                try:
                    await conn.execute("""
                        INSERT INTO community_users 
                        (email, username, full_name, role, country, organization, expertise_areas, bio)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (email) DO NOTHING
                    """, 
                    user_data['email'], user_data['username'], user_data['full_name'],
                    user_data['role'], user_data['country'], user_data['organization'],
                    user_data['expertise_areas'], user_data['bio'])
                    
                    logger.info(f"   ✅ Created test user: {user_data['username']}")
                except Exception as e:
                    logger.debug(f"   ⚠️ User {user_data['username']} might already exist: {e}")
            
            # Create test regional chapters with ambassadors
            user_ids = await conn.fetch("SELECT id, username FROM community_users")
            if user_ids:
                jamie_id = next((u['id'] for u in user_ids if u['username'] == 'jamie_founder'), None)
                
                if jamie_id:
                    await conn.execute("""
                        UPDATE regional_chapters 
                        SET ambassador_id = $1, member_count = 1
                        WHERE name = 'West Africa'
                    """, jamie_id)
                    logger.info("   📍 Assigned test ambassador to West Africa chapter")
            
            # Create a test community event
            await conn.execute("""
                INSERT INTO community_events 
                (title, description, type, start_time, end_time, organizer_id, is_virtual, is_published)
                VALUES 
                ('TAIFA-FIALA Community Launch Call', 
                 'Welcome to the TAIFA-FIALA community! Join us for an introduction to the platform and community guidelines.',
                 'call',
                 NOW() + INTERVAL '7 days',
                 NOW() + INTERVAL '7 days' + INTERVAL '1 hour',
                 $1,
                 TRUE,
                 TRUE)
                ON CONFLICT DO NOTHING
            """, jamie_id if jamie_id else 1)
            logger.info("   📅 Created test community event")
            
        await db.close()
        
        logger.info("✅ Test community data created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to create test data: {e}")

async def show_community_stats():
    """Display current community statistics"""
    try:
        from database.connector import DatabaseConnector
        
        db = DatabaseConnector()
        await db.initialize()
        
        logger.info("📊 Current Community Statistics:")
        logger.info("=" * 50)
        
        async with db.pool.acquire() as conn:
            # Get health metrics
            health = await conn.fetchrow("SELECT * FROM community_health_metrics")
            
            logger.info(f"👥 Active Users: {health['active_users']}")
            logger.info(f"🌍 Countries Represented: {health['countries_represented']}")
            logger.info(f"📝 Monthly Contributions: {health['monthly_contributions']}")
            logger.info(f"✅ Monthly Reviews: {health['monthly_reviews']}")
            logger.info(f"📖 Published Stories: {health['published_stories']}")
            if health['avg_review_rating']:
                logger.info(f"⭐ Average Review Rating: {health['avg_review_rating']:.2f}/5")
            
            # Get recent activity
            recent_activity = await conn.fetch("""
                SELECT activity_type, username, activity_subtype, created_at
                FROM recent_community_activity
                LIMIT 5
            """)
            
            if recent_activity:
                logger.info(f"\n🔄 Recent Activity:")
                for activity in recent_activity:
                    logger.info(f"   {activity['created_at'].strftime('%Y-%m-%d')} - "
                              f"{activity['username']}: {activity['activity_type']} "
                              f"({activity['activity_subtype']})")
            
            # Get top contributors
            top_contributors = await conn.fetch("""
                SELECT username, full_name, country, reputation_score, badge_count
                FROM community_leaderboard
                LIMIT 5
            """)
            
            if top_contributors:
                logger.info(f"\n🏆 Top Contributors:")
                for i, contributor in enumerate(top_contributors, 1):
                    logger.info(f"   {i}. {contributor['username']} "
                              f"({contributor['country']}) - "
                              f"Reputation: {contributor['reputation_score']}, "
                              f"Badges: {contributor['badge_count'] or 0}")
        
        await db.close()
        
    except Exception as e:
        logger.error(f"❌ Failed to get community stats: {e}")

async def main():
    """Main entry point for community schema management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TAIFA-FIALA Community Schema Management')
    parser.add_argument('--action', choices=['apply', 'test-data', 'stats'], 
                       default='apply', help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'apply':
        success = await apply_community_schema()
        if success:
            # Also create test data for development
            await create_test_community_data()
        return 0 if success else 1
        
    elif args.action == 'test-data':
        await create_test_community_data()
        return 0
        
    elif args.action == 'stats':
        await show_community_stats()
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)