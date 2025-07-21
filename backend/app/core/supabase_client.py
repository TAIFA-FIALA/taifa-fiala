"""
Supabase client configuration for proper authentication
"""
import os
import logging
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from backend directory
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)

# Configure logging
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_API_KEY')  # Use the service key for backend operations
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_PUBLISHABLE_KEY')  # This is the anon key for client-side

def create_supabase_client(use_service_key: bool = True) -> Optional[Client]:
    """
    Create a Supabase client with proper authentication.
    
    Args:
        use_service_key: If True, use the service key (for backend operations)
                        If False, use the anon key (for client-side operations)
    
    Returns:
        Supabase client instance or None if configuration is missing
    """
    if not SUPABASE_URL:
        logger.error("❌ SUPABASE_PROJECT_URL not found in environment variables")
        return None
    
    # Choose the appropriate key
    if use_service_key:
        api_key = SUPABASE_KEY
        key_type = "service"
    else:
        api_key = SUPABASE_ANON_KEY
        key_type = "anon"
    
    if not api_key:
        logger.error(f"❌ Supabase {key_type} key not found in environment variables")
        return None
    
    try:
        supabase_client = create_client(SUPABASE_URL, api_key)
        logger.info(f"✅ Supabase client created successfully with {key_type} key")
        return supabase_client
    except Exception as e:
        logger.error(f"❌ Failed to create Supabase client: {e}")
        return None

# Create a global client instance for backend operations
supabase_client = create_supabase_client(use_service_key=True)

async def test_supabase_connection():
    """Test the Supabase connection"""
    if not supabase_client:
        logger.error("❌ Supabase client not initialized")
        return False
    
    try:
        # Test connection by trying to access a simple table or making a basic query
        # This will use the Supabase API instead of direct database connection
        response = supabase_client.table('information_schema.tables').select('*').limit(1).execute()
        logger.info("✅ Supabase API connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Supabase API connection failed: {e}")
        return False

def get_supabase_client() -> Optional[Client]:
    """Get the global Supabase client instance"""
    return supabase_client

# Authentication helpers
def create_authenticated_client(access_token: str) -> Optional[Client]:
    """
    Create a Supabase client with user authentication token.
    
    Args:
        access_token: User's JWT access token
    
    Returns:
        Authenticated Supabase client instance
    """
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        logger.error("❌ Missing Supabase configuration for authenticated client")
        return None
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        # Set the auth token for this client
        client.auth.set_auth(access_token)
        logger.info("✅ Authenticated Supabase client created")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to create authenticated Supabase client: {e}")
        return None