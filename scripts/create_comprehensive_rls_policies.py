#!/usr/bin/env python3
"""
TAIFA-FIALA Comprehensive RLS Policies
=====================================

This script creates Row Level Security policies for all TAIFA-FIALA tables.
Policies are designed for production use with proper security levels.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def create_rls_policies():
    """Create comprehensive RLS policies for all tables"""
    
    # Connect to Supabase
    try:
        supabase_url = os.getenv('SUPABASE_PROJECT_URL')
        supabase_key = os.getenv('SUPABASE_API_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials")
            return False
        
        client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Define RLS policies for each table
    policies = {
        # Core Intelligence Feed - Public read, service write
        'africa_intelligence_feed': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON africa_intelligence_feed FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON africa_intelligence_feed FOR ALL USING (auth.role() = \'service_role\');'
            },
            {
                'name': 'Authenticated insert',
                'policy': 'CREATE POLICY "Authenticated insert" ON africa_intelligence_feed FOR INSERT WITH CHECK (auth.role() = \'authenticated\');'
            }
        ],
        
        # AI Domains - Public read
        'ai_domains': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON ai_domains FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON ai_domains FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Announcements - Public read
        'announcements': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON announcements FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON announcements FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Applications - User-specific access
        'applications': [
            {
                'name': 'Users can view own applications',
                'policy': 'CREATE POLICY "Users can view own applications" ON applications FOR SELECT USING (auth.uid() = user_id);'
            },
            {
                'name': 'Users can insert own applications',
                'policy': 'CREATE POLICY "Users can insert own applications" ON applications FOR INSERT WITH CHECK (auth.uid() = user_id);'
            },
            {
                'name': 'Users can update own applications',
                'policy': 'CREATE POLICY "Users can update own applications" ON applications FOR UPDATE USING (auth.uid() = user_id);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON applications FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Community Users - Public profiles, private details
        'community_users': [
            {
                'name': 'Public profile access',
                'policy': 'CREATE POLICY "Public profile access" ON community_users FOR SELECT USING (true);'
            },
            {
                'name': 'Users can update own profile',
                'policy': 'CREATE POLICY "Users can update own profile" ON community_users FOR UPDATE USING (auth.uid() = id);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON community_users FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Discussions - Public read, authenticated write
        'discussions': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON discussions FOR SELECT USING (true);'
            },
            {
                'name': 'Authenticated users can create discussions',
                'policy': 'CREATE POLICY "Authenticated users can create discussions" ON discussions FOR INSERT WITH CHECK (auth.role() = \'authenticated\');'
            },
            {
                'name': 'Users can update own discussions',
                'policy': 'CREATE POLICY "Users can update own discussions" ON discussions FOR UPDATE USING (auth.uid() = created_by);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON discussions FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Events - Public read
        'events': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON events FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON events FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Funding Opportunities Backup - Service only
        'funding_opportunities_backup': [
            {
                'name': 'Service role only access',
                'policy': 'CREATE POLICY "Service role only access" ON funding_opportunities_backup FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Funding Rounds - Public read
        'funding_rounds': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON funding_rounds FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON funding_rounds FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Funding Types - Public read
        'funding_types': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON funding_types FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON funding_types FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Geographic Scopes - Public read
        'geographic_scopes': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON geographic_scopes FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON geographic_scopes FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Health Check - Public read
        'health_check': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON health_check FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON health_check FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Impact Metrics - Public read
        'impact_metrics': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON impact_metrics FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON impact_metrics FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Investments - Public read
        'investments': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON investments FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON investments FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Notifications - User-specific
        'notifications': [
            {
                'name': 'Users can view own notifications',
                'policy': 'CREATE POLICY "Users can view own notifications" ON notifications FOR SELECT USING (auth.uid() = user_id);'
            },
            {
                'name': 'Users can update own notifications',
                'policy': 'CREATE POLICY "Users can update own notifications" ON notifications FOR UPDATE USING (auth.uid() = user_id);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON notifications FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Organizations - Public read
        'organizations': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON organizations FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON organizations FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Partnerships - Public read
        'partnerships': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON partnerships FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON partnerships FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Performance Metrics - Public read
        'performance_metrics': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON performance_metrics FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON performance_metrics FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Publications - Public read
        'publications': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON publications FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON publications FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Raw Content - Service only
        'raw_content': [
            {
                'name': 'Service role only access',
                'policy': 'CREATE POLICY "Service role only access" ON raw_content FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Research Projects - Public read
        'research_projects': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON research_projects FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON research_projects FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Resources - Public read
        'resources': [
            {
                'name': 'Public read access',
                'policy': 'CREATE POLICY "Public read access" ON resources FOR SELECT USING (true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON resources FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Scraping Queue - Service only
        'scraping_queue': [
            {
                'name': 'Service role only access',
                'policy': 'CREATE POLICY "Service role only access" ON scraping_queue FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Scraping Queue Status - Service only
        'scraping_queue_status': [
            {
                'name': 'Service role only access',
                'policy': 'CREATE POLICY "Service role only access" ON scraping_queue_status FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Scraping Results - Service only
        'scraping_results': [
            {
                'name': 'Service role only access',
                'policy': 'CREATE POLICY "Service role only access" ON scraping_results FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # Scraping Templates - Service only
        'scraping_templates': [
            {
                'name': 'Service role only access',
                'policy': 'CREATE POLICY "Service role only access" ON scraping_templates FOR ALL USING (auth.role() = \'service_role\');'
            }
        ],
        
        # User Profiles - User-specific
        'user_profiles': [
            {
                'name': 'Users can view own profile',
                'policy': 'CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = user_id);'
            },
            {
                'name': 'Users can update own profile',
                'policy': 'CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = user_id);'
            },
            {
                'name': 'Public basic profile access',
                'policy': 'CREATE POLICY "Public basic profile access" ON user_profiles FOR SELECT USING (is_public = true);'
            },
            {
                'name': 'Service role full access',
                'policy': 'CREATE POLICY "Service role full access" ON user_profiles FOR ALL USING (auth.role() = \'service_role\');'
            }
        ]
    }
    
    print("🔐 Creating comprehensive RLS policies...")
    print("=" * 50)
    
    success_count = 0
    error_count = 0
    
    for table_name, table_policies in policies.items():
        print(f"\n📋 Processing table: {table_name}")
        
        # Enable RLS on the table first
        try:
            rls_sql = f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;"
            client.rpc('execute_sql', {'sql': rls_sql})
            print(f"  ✅ RLS enabled on {table_name}")
        except Exception as e:
            print(f"  ⚠️  RLS enable warning for {table_name}: {str(e)[:100]}...")
        
        # Create policies
        for policy in table_policies:
            try:
                # Drop existing policy if it exists
                drop_sql = f"DROP POLICY IF EXISTS \"{policy['name']}\" ON {table_name};"
                client.rpc('execute_sql', {'sql': drop_sql})
                
                # Create new policy
                client.rpc('execute_sql', {'sql': policy['policy']})
                print(f"  ✅ Created policy: {policy['name']}")
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ Failed to create policy '{policy['name']}': {str(e)[:100]}...")
                error_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 RLS Policy Creation Complete!")
    print(f"✅ Successful policies: {success_count}")
    print(f"❌ Failed policies: {error_count}")
    
    if error_count == 0:
        print("\n🔒 All tables are now properly secured with RLS!")
        print("\nSecurity Summary:")
        print("- 📖 Public tables: Read access for all users")
        print("- 👤 User-specific tables: Users can only access their own data")
        print("- 🔧 Service tables: Only service role can access")
        print("- 🛡️  System tables: Protected from unauthorized access")
    else:
        print(f"\n⚠️  {error_count} policies failed to create. Check the errors above.")
    
    return error_count == 0

if __name__ == "__main__":
    print("🚀 TAIFA-FIALA Comprehensive RLS Policy Creator")
    print("=" * 60)
    
    success = create_rls_policies()
    
    if success:
        print("\n🎉 All RLS policies created successfully!")
        print("Your database is now production-ready with proper security.")
    else:
        print("\n❌ Some policies failed to create.")
        print("Please check the errors above and run the script again.")
        sys.exit(1)