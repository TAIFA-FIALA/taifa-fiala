"""
Source Validator Module

Handles initial validation of submitted funding sources including accessibility checks,
content relevance assessment, and authority verification.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser

from app.core.database import get_database
from app.utils.url_utils import normalize_url
from app.services.ETL_pipelines.serper_search import SerperSearch


@dataclass
class SourceSubmission:
    """Data structure for source submissions"""
    name: str
    url: str
    contact_person: str
    contact_email: str
    source_type: str  # rss_feed, newsletter, webpage, api, other
    update_frequency: str  # daily, weekly, monthly, ad_hoc
    geographic_focus: List[str]
    expected_volume: str  # 1-5, 5-20, 20+ per month
    sample_urls: List[str]
    ai_relevance_estimate: int  # percentage
    africa_relevance_estimate: int  # percentage
    language: str
    submitter_role: str
    has_permission: bool
    preferred_contact: str
    submitted_at: datetime


@dataclass
class ValidationResult:
    """Result of source validation"""
    validation_score: float
    recommendation: str  # accept, reject, needs_review
    checks: Dict[str, Any]
    issues: List[str]
    suggestions: List[str]


class SourceValidator:
    """Main source validation class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.serper = SerperSearch()
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'TAIFA-Bot/1.0 (Funding Tracker; +https://taifa-africa.com)'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def validate_submission(self, submission: SourceSubmission) -> ValidationResult:
        """
        Main validation method that runs all checks on a submitted source
        
        Args:
            submission: SourceSubmission object with all source details
            
        Returns:
            ValidationResult with validation score and recommendations
        """
        self.logger.info(f"Starting validation for source: {submission.name}")
        
        # Run all validation checks
        checks = {
            "url_accessible": await self._check_url_accessibility(submission.url),
            "content_relevant": await self._assess_content_relevance(submission),
            "update_frequency": await self._verify_update_frequency(submission.url),
            "authority_confirmed": self._verify_submitter_authority(submission),
            "robots_txt_compliant": await self._check_robots_txt_compliance(submission.url),
            "no_duplicate_source": await self._check_existing_sources(submission.url),
            "technical_feasibility": await self._assess_technical_feasibility(submission),
            "sample_quality": await self._validate_sample_urls(submission.sample_urls)
        }
        
        # Calculate validation score
        score = self._calculate_validation_score(checks)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(score, checks)
        
        # Identify issues and suggestions
        issues = self._identify_issues(checks)
        suggestions = self._generate_suggestions(checks, submission)
        
        result = ValidationResult(
            validation_score=score,
            recommendation=recommendation,
            checks=checks,
            issues=issues,
            suggestions=suggestions
        )
        
        self.logger.info(f"Validation complete for {submission.name}: {score:.2f} ({recommendation})")
        return result
    
    async def _check_url_accessibility(self, url: str) -> Dict[str, Any]:
        """Check if the URL is accessible and returns valid content"""
        try:
            async with self.session.get(url) as response:
                return {
                    "accessible": True,
                    "status_code": response.status,
                    "content_type": response.headers.get('content-type', ''),
                    "content_length": len(await response.text()),
                    "response_time": response.headers.get('x-response-time', 'unknown')
                }
        except Exception as e:
            return {
                "accessible": False,
                "error": str(e),
                "status_code": None,
                "content_type": None,
                "content_length": 0
            }
    
    async def _assess_content_relevance(self, submission: SourceSubmission) -> Dict[str, Any]:
        """Assess the relevance of content to AI and Africa"""
        try:
            # Fetch and analyze main page content
            async with self.session.get(submission.url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract text content
                text_content = soup.get_text()
                
                # Look for AI-related keywords
                ai_keywords = [
                    'artificial intelligence', 'machine learning', 'ai', 'ml', 
                    'deep learning', 'neural network', 'data science', 'automation',
                    'robotics', 'computer vision', 'natural language processing'
                ]
                
                # Look for Africa-related keywords
                africa_keywords = [
                    'africa', 'african', 'nigeria', 'kenya', 'south africa', 'ghana',
                    'ethiopia', 'morocco', 'uganda', 'tanzania', 'zimbabwe', 'botswana',
                    'rwanda', 'senegal', 'côte d\'ivoire', 'ivory coast', 'egypt'
                ]
                
                # Look for funding-related keywords
                funding_keywords = [
                    'grant', 'funding', 'scholarship', 'award', 'prize', 'fellowship',
                    'research funding', 'innovation fund', 'development fund', 'investment'
                ]
                
                text_lower = text_content.lower()
                
                ai_score = sum(1 for keyword in ai_keywords if keyword in text_lower) / len(ai_keywords)
                africa_score = sum(1 for keyword in africa_keywords if keyword in text_lower) / len(africa_keywords)
                funding_score = sum(1 for keyword in funding_keywords if keyword in text_lower) / len(funding_keywords)
                
                return {
                    "relevant": True,
                    "ai_relevance_score": min(ai_score * 2, 1.0),  # Scale up but cap at 1.0
                    "africa_relevance_score": min(africa_score * 3, 1.0),
                    "funding_relevance_score": min(funding_score * 2, 1.0),
                    "overall_relevance": (ai_score + africa_score + funding_score) / 3,
                    "content_length": len(text_content),
                    "has_recent_content": self._check_for_recent_dates(text_content)
                }
                
        except Exception as e:
            return {
                "relevant": False,
                "error": str(e),
                "ai_relevance_score": 0,
                "africa_relevance_score": 0,
                "funding_relevance_score": 0,
                "overall_relevance": 0
            }
    
    async def _verify_update_frequency(self, url: str) -> Dict[str, Any]:
        """Verify how frequently the source is updated"""
        try:
            # Check if it's an RSS feed
            if 'rss' in url.lower() or 'feed' in url.lower():
                return await self._check_rss_frequency(url)
            
            # For web pages, check for date patterns and freshness
            async with self.session.get(url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Look for date patterns
                dates_found = self._extract_dates_from_content(soup.get_text())
                
                if dates_found:
                    latest_date = max(dates_found)
                    days_since_update = (datetime.now() - latest_date).days
                    
                    if days_since_update <= 7:
                        frequency = "weekly_or_more"
                    elif days_since_update <= 30:
                        frequency = "monthly"
                    elif days_since_update <= 90:
                        frequency = "quarterly"
                    else:
                        frequency = "infrequent"
                    
                    return {
                        "frequency_detected": True,
                        "estimated_frequency": frequency,
                        "latest_update": latest_date.isoformat(),
                        "days_since_update": days_since_update,
                        "dates_found": len(dates_found)
                    }
                
                return {
                    "frequency_detected": False,
                    "estimated_frequency": "unknown",
                    "dates_found": 0
                }
                
        except Exception as e:
            return {
                "frequency_detected": False,
                "error": str(e),
                "estimated_frequency": "unknown"
            }
    
    async def _check_rss_frequency(self, rss_url: str) -> Dict[str, Any]:
        """Check RSS feed update frequency"""
        try:
            import feedparser
            
            feed = feedparser.parse(rss_url)
            
            if feed.entries:
                # Get publication dates from recent entries
                pub_dates = []
                for entry in feed.entries[:10]:  # Check last 10 entries
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_dates.append(datetime(*entry.published_parsed[:6]))
                
                if len(pub_dates) >= 2:
                    # Calculate average time between posts
                    intervals = []
                    for i in range(1, len(pub_dates)):
                        interval = abs((pub_dates[i-1] - pub_dates[i]).days)
                        intervals.append(interval)
                    
                    avg_interval = sum(intervals) / len(intervals)
                    
                    if avg_interval <= 1:
                        frequency = "daily"
                    elif avg_interval <= 7:
                        frequency = "weekly"
                    elif avg_interval <= 30:
                        frequency = "monthly"
                    else:
                        frequency = "infrequent"
                    
                    return {
                        "is_rss": True,
                        "entries_found": len(feed.entries),
                        "recent_entries": len(pub_dates),
                        "estimated_frequency": frequency,
                        "average_interval_days": avg_interval,
                        "last_updated": pub_dates[0].isoformat() if pub_dates else None
                    }
            
            return {
                "is_rss": True,
                "entries_found": len(feed.entries) if feed.entries else 0,
                "estimated_frequency": "unknown",
                "error": "No dated entries found"
            }
            
        except Exception as e:
            return {
                "is_rss": False,
                "error": str(e),
                "estimated_frequency": "unknown"
            }
    
    def _verify_submitter_authority(self, submission: SourceSubmission) -> Dict[str, Any]:
        """Verify if submitter has authority to authorize monitoring"""
        # Check email domain matches source domain
        email_domain = submission.contact_email.split('@')[-1].lower()
        source_domain = urlparse(submission.url).netloc.lower()
        
        # Remove 'www.' prefix for comparison
        if source_domain.startswith('www.'):
            source_domain = source_domain[4:]
        
        domain_match = email_domain == source_domain
        
        # Check for institutional roles
        institutional_roles = [
            'research', 'funding', 'grants', 'admin', 'manager', 
            'director', 'coordinator', 'officer', 'staff'
        ]
        
        has_institutional_role = any(
            role in submission.submitter_role.lower() 
            for role in institutional_roles
        )
        
        return {
            "domain_match": domain_match,
            "has_permission": submission.has_permission,
            "has_institutional_role": has_institutional_role,
            "submitter_email_domain": email_domain,
            "source_domain": source_domain,
            "authority_score": (
                (0.4 if domain_match else 0) +
                (0.4 if submission.has_permission else 0) +
                (0.2 if has_institutional_role else 0)
            )
        }
    
    async def _check_robots_txt_compliance(self, url: str) -> Dict[str, Any]:
        """Check if we can legally scrape this source"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    
                    # Parse robots.txt
                    rp = RobotFileParser()
                    rp.set_url(robots_url)
                    rp.set_content(robots_content)
                    
                    # Check if our user agent can fetch the URL
                    can_fetch = rp.can_fetch('TAIFA-Bot', url)
                    
                    return {
                        "robots_txt_exists": True,
                        "can_fetch": can_fetch,
                        "robots_url": robots_url,
                        "compliant": can_fetch
                    }
                else:
                    # No robots.txt means we can proceed
                    return {
                        "robots_txt_exists": False,
                        "can_fetch": True,
                        "compliant": True
                    }
                    
        except Exception as e:
            return {
                "robots_txt_exists": False,
                "can_fetch": True,  # Assume we can if check fails
                "compliant": True,
                "error": str(e)
            }
    
    async def _check_existing_sources(self, url: str) -> Dict[str, Any]:
        """Check if this source is already being monitored"""
        try:
            # Normalize URL for comparison
            normalized_url = normalize_url(url)
            
            # Check database for existing sources
            db = await get_database()
            existing_sources = await db.fetch_all(
                "SELECT id, name, url FROM data_sources WHERE url = :url OR url = :normalized_url",
                {"url": url, "normalized_url": normalized_url}
            )
            
            if existing_sources:
                return {
                    "is_duplicate": True,
                    "existing_sources": [
                        {"id": row["id"], "name": row["name"], "url": row["url"]}
                        for row in existing_sources
                    ]
                }
            
            # Check for similar domains
            parsed_url = urlparse(normalized_url)
            domain = parsed_url.netloc
            
            similar_sources = await db.fetch_all(
                "SELECT id, name, url FROM data_sources WHERE url LIKE :domain_pattern",
                {"domain_pattern": f"%{domain}%"}
            )
            
            return {
                "is_duplicate": False,
                "similar_sources": [
                    {"id": row["id"], "name": row["name"], "url": row["url"]}
                    for row in similar_sources
                ] if similar_sources else []
            }
            
        except Exception as e:
            return {
                "is_duplicate": False,
                "error": str(e),
                "similar_sources": []
            }
    
    async def _assess_technical_feasibility(self, submission: SourceSubmission) -> Dict[str, Any]:
        """Assess how technically feasible it is to monitor this source"""
        source_type = submission.source_type.lower()
        
        feasibility_scores = {
            "rss_feed": 1.0,
            "api": 0.9,
            "newsletter": 0.7,
            "webpage": 0.6,
            "other": 0.3
        }
        
        base_score = feasibility_scores.get(source_type, 0.5)
        
        # Adjust based on update frequency
        frequency_adjustments = {
            "daily": 0.0,
            "weekly": 0.1,
            "monthly": 0.2,
            "ad_hoc": -0.2
        }
        
        freq_adjustment = frequency_adjustments.get(submission.update_frequency, 0)
        
        # Adjust based on expected volume
        volume_adjustments = {
            "1-5": 0.1,
            "5-20": 0.0,
            "20+": -0.1
        }
        
        vol_adjustment = volume_adjustments.get(submission.expected_volume, 0)
        
        final_score = min(base_score + freq_adjustment + vol_adjustment, 1.0)
        
        return {
            "feasible": final_score > 0.5,
            "feasibility_score": final_score,
            "source_type": source_type,
            "base_score": base_score,
            "adjustments": {
                "frequency": freq_adjustment,
                "volume": vol_adjustment
            },
            "complexity": "low" if final_score > 0.8 else "medium" if final_score > 0.6 else "high"
        }
    
    async def _validate_sample_urls(self, sample_urls: List[str]) -> Dict[str, Any]:
        """Validate the quality of sample URLs provided"""
        if not sample_urls:
            return {
                "samples_provided": False,
                "valid_samples": 0,
                "sample_quality": 0
            }
        
        valid_samples = 0
        sample_analyses = []
        
        for url in sample_urls[:3]:  # Limit to first 3 samples
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        text_content = soup.get_text()
                        
                        # Basic quality checks
                        has_funding_keywords = any(
                            keyword in text_content.lower() 
                            for keyword in ['grant', 'funding', 'scholarship', 'award', 'fellowship']
                        )
                        
                        has_amount = any(
                            char in text_content for char in ['$', '€', '£', '₦', 'USD', 'EUR']
                        )
                        
                        has_deadline = any(
                            keyword in text_content.lower()
                            for keyword in ['deadline', 'due date', 'application', 'submit']
                        )
                        
                        if has_funding_keywords and (has_amount or has_deadline):
                            valid_samples += 1
                            
                        sample_analyses.append({
                            "url": url,
                            "accessible": True,
                            "has_funding_keywords": has_funding_keywords,
                            "has_amount": has_amount,
                            "has_deadline": has_deadline,
                            "content_length": len(text_content)
                        })
                        
            except Exception as e:
                sample_analyses.append({
                    "url": url,
                    "accessible": False,
                    "error": str(e)
                })
        
        return {
            "samples_provided": True,
            "total_samples": len(sample_urls),
            "valid_samples": valid_samples,
            "sample_quality": valid_samples / len(sample_urls) if sample_urls else 0,
            "sample_analyses": sample_analyses
        }
    
    def _calculate_validation_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall validation score based on check results"""
        weights = {
            "url_accessible": 0.20,
            "content_relevant": 0.25,
            "authority_confirmed": 0.15,
            "robots_txt_compliant": 0.10,
            "no_duplicate_source": 0.15,
            "technical_feasibility": 0.10,
            "sample_quality": 0.05
        }
        
        scores = {}
        
        # Convert check results to scores
        scores["url_accessible"] = 1.0 if checks["url_accessible"]["accessible"] else 0.0
        scores["content_relevant"] = checks["content_relevant"]["overall_relevance"]
        scores["authority_confirmed"] = checks["authority_confirmed"]["authority_score"]
        scores["robots_txt_compliant"] = 1.0 if checks["robots_txt_compliant"]["compliant"] else 0.0
        scores["no_duplicate_source"] = 0.0 if checks["no_duplicate_source"]["is_duplicate"] else 1.0
        scores["technical_feasibility"] = checks["technical_feasibility"]["feasibility_score"]
        scores["sample_quality"] = checks["sample_quality"]["sample_quality"]
        
        # Calculate weighted average
        total_score = sum(scores[key] * weights[key] for key in weights.keys())
        
        return total_score
    
    def _generate_recommendation(self, score: float, checks: Dict[str, Any]) -> str:
        """Generate recommendation based on validation score and specific issues"""
        if score >= 0.8:
            return "accept"
        elif score >= 0.6:
            # Check for critical issues
            if not checks["url_accessible"]["accessible"]:
                return "reject"
            if checks["no_duplicate_source"]["is_duplicate"]:
                return "reject"
            if not checks["robots_txt_compliant"]["compliant"]:
                return "reject"
            return "needs_review"
        else:
            return "reject"
    
    def _identify_issues(self, checks: Dict[str, Any]) -> List[str]:
        """Identify specific issues with the submission"""
        issues = []
        
        if not checks["url_accessible"]["accessible"]:
            issues.append(f"URL not accessible: {checks['url_accessible'].get('error', 'Unknown error')}")
        
        if checks["content_relevant"]["overall_relevance"] < 0.3:
            issues.append("Content appears to have low relevance to AI funding in Africa")
        
        if checks["authority_confirmed"]["authority_score"] < 0.5:
            issues.append("Submitter authority unclear - email domain doesn't match source")
        
        if not checks["robots_txt_compliant"]["compliant"]:
            issues.append("Robots.txt disallows automated access")
        
        if checks["no_duplicate_source"]["is_duplicate"]:
            issues.append("Source is already being monitored")
        
        if checks["technical_feasibility"]["feasibility_score"] < 0.5:
            issues.append("Technical monitoring appears challenging")
        
        if checks["sample_quality"]["sample_quality"] < 0.5:
            issues.append("Sample URLs provided are of poor quality or not funding-related")
        
        return issues
    
    def _generate_suggestions(self, checks: Dict[str, Any], submission: SourceSubmission) -> List[str]:
        """Generate helpful suggestions for improvement"""
        suggestions = []
        
        if checks["authority_confirmed"]["authority_score"] < 0.8:
            suggestions.append("Consider having a staff member from the organization submit this source")
        
        if checks["content_relevant"]["ai_relevance_score"] < 0.5:
            suggestions.append("Ensure the source specifically covers AI/ML intelligence feed")
        
        if checks["technical_feasibility"]["feasibility_score"] < 0.7:
            if submission.source_type == "webpage":
                suggestions.append("Check if the organization offers RSS feeds or email newsletters")
        
        if checks["sample_quality"]["sample_quality"] < 0.8:
            suggestions.append("Provide more specific URLs to intelligence item pages rather than general pages")
        
        return suggestions
    
    def _check_for_recent_dates(self, text: str) -> bool:
        """Check if content contains recent dates"""
        import re
        
        # Look for year patterns
        current_year = datetime.now().year
        year_pattern = r'\b(202[0-9])\b'
        years_found = re.findall(year_pattern, text)
        
        if years_found:
            latest_year = max(int(year) for year in years_found)
            return latest_year >= current_year - 1
        
        return False
    
    def _extract_dates_from_content(self, text: str) -> List[datetime]:
        """Extract dates from text content"""
        import re
        from dateutil.parser import parse
        
        dates = []
        
        # Common date patterns
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # YYYY/MM/DD
            r'\b[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    parsed_date = parse(match)
                    if parsed_date.year >= 2020:  # Only consider recent dates
                        dates.append(parsed_date)
                except:
                    continue
        
        return sorted(dates, reverse=True)
