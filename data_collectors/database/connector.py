import asyncio
import asyncpg
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import aiohttp

logger = logging.getLogger(__name__)

class DatabaseConnector:
    """Database connector with DeepSeek AI parsing fallback"""
    
    def __init__(self):
        load_dotenv()
        self.database_url = os.getenv("DATABASE_URL")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.pool = None
        self.deepseek_session = None
        
    async def initialize(self):
        """Initialize database connection pool and DeepSeek session"""
        try:
            # Initialize database pool
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            logger.info("✅ Database connection pool initialized")
            
            # Initialize DeepSeek session
            if self.deepseek_api_key:
                self.deepseek_session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={
                        'Authorization': f'Bearer {self.deepseek_api_key}',
                        'Content-Type': 'application/json'
                    }
                )
                logger.info("✅ DeepSeek AI session initialized")
            else:
                logger.warning("⚠️  DeepSeek API key not found - AI parsing disabled")
                
            await self._ensure_tables_exist()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database connector: {e}")
            raise
    
    async def close(self):
        """Close database pool and DeepSeek session"""
        if self.pool:
            await self.pool.close()
        if self.deepseek_session:
            await self.deepseek_session.close()
    
    async def _ensure_tables_exist(self):
        """Ensure required tables exist"""
        async with self.pool.acquire() as conn:
            # Create opportunities table if it doesn't exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS funding_opportunities (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    source_url TEXT UNIQUE NOT NULL,
                    organization_name TEXT,
                    funding_amount TEXT,
                    deadline DATE,
                    application_url TEXT,
                    
                    -- Source tracking
                    source_type TEXT NOT NULL, -- 'rss' or 'serper_search'
                    source_name TEXT NOT NULL,
                    search_query TEXT,
                    
                    -- Relevance scoring
                    ai_relevance_score REAL DEFAULT 0.0,
                    africa_relevance_score REAL DEFAULT 0.0,
                    funding_relevance_score REAL DEFAULT 0.0,
                    overall_relevance_score REAL DEFAULT 0.0,
                    
                    -- Metadata
                    content_hash TEXT UNIQUE NOT NULL,
                    raw_data JSONB,
                    discovered_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    
                    -- Processing flags
                    parsed_with_ai BOOLEAN DEFAULT FALSE,
                    verified BOOLEAN DEFAULT FALSE,
                    active BOOLEAN DEFAULT TRUE
                );
                
                CREATE INDEX IF NOT EXISTS idx_content_hash ON funding_opportunities(content_hash);
                CREATE INDEX IF NOT EXISTS idx_source_type ON funding_opportunities(source_type);
                CREATE INDEX IF NOT EXISTS idx_relevance_score ON funding_opportunities(overall_relevance_score);
                CREATE INDEX IF NOT EXISTS idx_discovered_date ON funding_opportunities(discovered_date);
            """)
            
            logger.info("✅ Database tables verified/created")
    
    async def save_opportunities(self, opportunities: List[Dict[str, Any]], source_type: str) -> Dict[str, int]:
        """Save opportunities to database with duplicate detection"""
        results = {
            "saved": 0,
            "duplicates": 0,
            "errors": 0,
            "ai_parsed": 0
        }
        
        async with self.pool.acquire() as conn:
            for opp in opportunities:
                try:
                    # Check for duplicates by content hash
                    existing = await conn.fetchrow(
                        "SELECT id FROM funding_opportunities WHERE content_hash = $1",
                        opp.get("content_hash")
                    )
                    
                    if existing:
                        results["duplicates"] += 1
                        continue
                    
                    # Try deterministic parsing first
                    try:
                        parsed_opp = await self._parse_opportunity_deterministic(opp)
                        parsed_with_ai = False
                    except Exception as e:
                        logger.warning(f"Deterministic parsing failed: {e}")
                        # Fallback to DeepSeek AI parsing
                        parsed_opp = await self._parse_opportunity_with_deepseek(opp)
                        parsed_with_ai = True
                        results["ai_parsed"] += 1
                        logger.info("✨ Used DeepSeek AI parsing fallback")
                    
                    # Insert opportunity
                    await conn.execute("""
                        INSERT INTO funding_opportunities (
                            title, description, source_url, organization_name,
                            funding_amount, deadline, application_url,
                            source_type, source_name, search_query,
                            ai_relevance_score, africa_relevance_score,
                            funding_relevance_score, overall_relevance_score,
                            content_hash, raw_data, parsed_with_ai
                        ) VALUES (
                            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                            $11, $12, $13, $14, $15, $16, $17
                        )
                    """, 
                        parsed_opp["title"],
                        parsed_opp["description"],
                        parsed_opp["source_url"],
                        parsed_opp.get("organization_name"),
                        parsed_opp.get("funding_amount"),
                        parsed_opp.get("deadline"),
                        parsed_opp.get("application_url"),
                        source_type,
                        parsed_opp.get("source_name", ""),
                        parsed_opp.get("search_query", ""),
                        parsed_opp.get("ai_relevance_score", 0.0),
                        parsed_opp.get("africa_relevance_score", 0.0), 
                        parsed_opp.get("funding_relevance_score", 0.0),
                        parsed_opp.get("overall_relevance_score", 0.0),
                        parsed_opp["content_hash"],
                        json.dumps(opp),
                        parsed_with_ai
                    )
                    
                    results["saved"] += 1
                    
                except Exception as e:
                    logger.error(f"Error saving opportunity '{opp.get('title', 'Unknown')}': {e}")
                    results["errors"] += 1
        
        logger.info(f"💾 Database save results: {results}")
        return results
    
    async def _parse_opportunity_deterministic(self, opp: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic parsing - fast but may fail on complex content"""
        
        # Basic field extraction
        parsed = {
            "title": opp.get("title", "").strip(),
            "description": opp.get("description", "").strip(),
            "source_url": opp.get("source_url", "").strip(),
            "content_hash": opp.get("content_hash", ""),
            "source_name": opp.get("search_query", ""),
            "search_query": opp.get("search_query", ""),
            "ai_relevance_score": opp.get("ai_relevance_score", 0.0),
            "africa_relevance_score": opp.get("africa_relevance_score", 0.0),
            "funding_relevance_score": opp.get("funding_relevance_score", 0.0),
            "overall_relevance_score": opp.get("overall_relevance_score", 0.0)
        }
        
        # Extract funding amount using regex patterns
        text = f"{parsed['title']} {parsed['description']}".lower()
        
        # Funding amount patterns
        import re
        amount_patterns = [
            r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|thousand|k|m|b))?',
            r'[\d,]+(?:\.\d{2})?\s*(?:USD|EUR|GBP|dollars?|euros?|pounds?)',
            r'up to \$?[\d,]+',
            r'grant of \$?[\d,]+',
            r'[\d,]+\s*million\s*(?:USD|dollars?|naira|rand)',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed["funding_amount"] = match.group(0)
                break
        
        # Extract organization from domain or title
        if "idrc" in text or "crdi" in text:
            parsed["organization_name"] = "IDRC (International Development Research Centre)"
        elif "science for africa" in text:
            parsed["organization_name"] = "Science for Africa Foundation"
        elif "gates" in text:
            parsed["organization_name"] = "Gates Foundation"
        elif "milken" in text:
            parsed["organization_name"] = "Milken Institute"
        
        # Simple deadline detection
        deadline_keywords = ["deadline", "due", "apply by", "closes", "expires", "until", "before"]
        has_deadline = any(keyword in text for keyword in deadline_keywords)
        
        # If content seems complex or has deadline info, raise error to trigger AI parsing
        if has_deadline and not parsed.get("funding_amount"):
            raise ValueError("Complex content detected - needs AI parsing")
        
        return parsed
    
    async def _parse_opportunity_with_deepseek(self, opp: Dict[str, Any]) -> Dict[str, Any]:
        """Use DeepSeek AI for robust parsing of complex content"""
        
        if not self.deepseek_session:
            logger.warning("DeepSeek session not available, using basic parsing")
            return await self._parse_opportunity_deterministic(opp)
        
        try:
            # Prepare content for AI parsing
            content = f"""
            Title: {opp.get('title', '')}
            Description: {opp.get('description', '')}
            URL: {opp.get('source_url', '')}
            """
            
            prompt = f"""Parse this funding opportunity and extract structured information. 
            Return JSON only with these fields:
            {{
                "organization_name": "name of funding organization",
                "funding_amount": "amount if mentioned (e.g. '$50,000', '10 million USD')",
                "deadline": "deadline date if mentioned (YYYY-MM-DD format or null)",
                "application_url": "application URL if different from source URL",
                "key_focus_areas": ["list", "of", "key", "focus", "areas"]
            }}
            
            Content to parse:
            {content}
            
            Return only valid JSON, no other text."""
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
            
            async with self.deepseek_session.post(
                "https://api.deepseek.com/chat/completions",
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    ai_content = result["choices"][0]["message"]["content"].strip()
                    
                    # Try to parse JSON response
                    try:
                        ai_parsed = json.loads(ai_content)
                        
                        # Merge AI results with original data
                        parsed = await self._parse_opportunity_deterministic(opp)
                        
                        # Override with AI-extracted data where available
                        if ai_parsed.get("organization_name"):
                            parsed["organization_name"] = ai_parsed["organization_name"]
                        if ai_parsed.get("funding_amount"):
                            parsed["funding_amount"] = ai_parsed["funding_amount"]
                        if ai_parsed.get("application_url"):
                            parsed["application_url"] = ai_parsed["application_url"]
                            
                        # Try to parse deadline
                        if ai_parsed.get("deadline") and ai_parsed["deadline"] != "null":
                            try:
                                from datetime import datetime
                                parsed["deadline"] = datetime.fromisoformat(ai_parsed["deadline"]).date()
                            except:
                                pass  # Invalid date format, skip
                        
                        logger.info("✨ Successfully parsed with DeepSeek AI")
                        return parsed
                        
                    except json.JSONDecodeError:
                        logger.warning("DeepSeek returned invalid JSON, using basic parsing")
                        
                else:
                    logger.warning(f"DeepSeek API error {response.status}")
                    
        except Exception as e:
            logger.error(f"DeepSeek parsing failed: {e}")
        
        # Fallback to deterministic parsing
        return await self._parse_opportunity_deterministic(opp)
    
    async def get_recent_opportunities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent opportunities from database"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    id, title, description, source_url, organization_name,
                    funding_amount, deadline, application_url,
                    source_type, source_name, search_query,
                    ai_relevance_score, africa_relevance_score,
                    funding_relevance_score, overall_relevance_score,
                    discovered_date, parsed_with_ai
                FROM funding_opportunities 
                WHERE active = true
                ORDER BY discovered_date DESC 
                LIMIT $1
            """, limit)
            
            return [dict(row) for row in rows]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics"""
        async with self.pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_opportunities,
                    COUNT(*) FILTER (WHERE source_type = 'rss') as rss_opportunities,
                    COUNT(*) FILTER (WHERE source_type = 'serper_search') as serper_opportunities,
                    COUNT(*) FILTER (WHERE parsed_with_ai = true) as ai_parsed_opportunities,
                    AVG(overall_relevance_score) as avg_relevance_score,
                    COUNT(*) FILTER (WHERE discovered_date >= NOW() - INTERVAL '24 hours') as today_opportunities,
                    COUNT(*) FILTER (WHERE discovered_date >= NOW() - INTERVAL '7 days') as week_opportunities
                FROM funding_opportunities 
                WHERE active = true
            """)
            
            return dict(stats)