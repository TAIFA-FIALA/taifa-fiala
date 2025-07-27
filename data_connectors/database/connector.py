import asyncio
import asyncpg
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import aiohttp
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class DatabaseConnector:
    """Database connector with DeepSeek AI parsing fallback"""
    
    def __init__(self, supabase_client, settings):
        self.supabase = supabase_client
        self.settings = settings
        self.deepseek_api_key = settings.DEEPSEEK_API_KEY
        self.deepseek_session = None
        
        # Add tracking for duplicates
        self.duplicates_count = 0

    async def initialize(self):
        """Initialize DeepSeek session"""
        try:
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
                
            # Test Supabase connection
            if self.supabase:
                try:
                    response = self.supabase.table('africa_intelligence_feed').select('id').limit(1).execute()
                    logger.info("✅ Database connection successful")
                except Exception as e:
                    logger.error(f"❌ Database connection test failed: {e}")
                    # Don't raise here, we'll handle it with retry logic
            else:
                logger.error("❌ Supabase client not provided")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize database connector: {e}")
            raise
            
    async def connect_with_retry(self, max_retries=3, retry_delay=5):
        """Connect to database with retry logic"""
        for attempt in range(max_retries):
            try:
                # Test connection
                if self.supabase:
                    response = self.supabase.table('africa_intelligence_feed').select('id').limit(1).execute()
                    logger.info(f"✅ Database connection successful on attempt {attempt+1}/{max_retries}")
                    return True
                else:
                    logger.error("❌ Supabase client not provided")
                    return False
            except Exception as e:
                logger.error(f"Database connection attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("All database connection attempts failed")
                    return False
        return False

    async def close(self):
        """Close DeepSeek session"""
        if self.deepseek_session:
            await self.deepseek_session.close()

    async def save_opportunities(self, opportunities: List[Dict[str, Any]], source_type: str) -> Dict[str, Any]:
        """Save opportunities to database with duplicate detection using Supabase"""
        results = {
            "saved": 0,
            "duplicates": 0,
            "errors": 0,
            "ai_parsed": 0,
            "opportunity_ids": []
        }

        for opp in opportunities:
            try:
                # Check for duplicates by content hash
                response = self.supabase.table('africa_intelligence_feed').select('id').eq('content_hash', opp.get("content_hash")).execute()
                if response.data:
                    results["duplicates"] += 1
                    self.duplicates_count += 1
                    logger.info(f"Duplicate detected: {opp.get('title', 'Unknown')[:50]}...")
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
                insert_data = {
                    "title": parsed_opp["title"],
                    "description": parsed_opp["description"],
                    "source_url": parsed_opp["source_url"],
                    "organization_name": parsed_opp.get("organization_name"),
                    "funding_amount": parsed_opp.get("funding_amount"),
                    "deadline": parsed_opp.get("deadline"),
                    "application_url": parsed_opp.get("application_url"),
                    "source_type": source_type,
                    "source_name": parsed_opp.get("source_name", ""),
                    "search_query": parsed_opp.get("search_query", ""),
                    "ai_relevance_score": parsed_opp.get("ai_relevance_score", 0.0),
                    "africa_relevance_score": parsed_opp.get("africa_relevance_score", 0.0),
                    "funding_relevance_score": parsed_opp.get("funding_relevance_score", 0.0),
                    "overall_relevance_score": parsed_opp.get("overall_relevance_score", 0.0),
                    "content_hash": parsed_opp["content_hash"],
                    "raw_data": json.dumps(opp),
                    "parsed_with_ai": parsed_with_ai
                }
                response = self.supabase.table('africa_intelligence_feed').insert(insert_data).execute()

                if response.data:
                    results["saved"] += 1
                    results["opportunity_ids"].append(response.data[0]['id'])
                else:
                    results["errors"] += 1

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
            
            prompt = f"""Parse this intelligence item and extract structured information. 
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
                FROM africa_intelligence_feed 
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
                FROM africa_intelligence_feed 
                WHERE active = true
            """)
            
            return dict(stats)