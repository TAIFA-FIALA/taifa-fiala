"""
URL Utilities for Source Validation

Helper functions for URL processing, normalization, and validation used
throughout the source validation module.
"""

import re
import hashlib
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Optional, Dict, List, Tuple


def normalize_url(url: str) -> str:
    """
    Normalize URL for consistent comparison and deduplication
    
    Args:
        url: Raw URL string
        
    Returns:
        Normalized URL string
    """
    if not url:
        return ""
    
    try:
        # Parse the URL
        parsed = urlparse(url.lower().strip())
        
        # Default scheme to https if missing
        scheme = parsed.scheme or 'https'
        
        # Remove common tracking parameters
        tracking_params = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
            'fbclid', 'gclid', 'ref', 'source', 'campaign_id', '_ga', 'mc_cid',
            'mc_eid', 'eid', 'hash', 'ref_src', 'ref_url', 'ss_source', 'ss_campaign'
        }
        
        # Parse and filter query parameters
        query_params = parse_qs(parsed.query)
        filtered_params = {
            k: v for k, v in query_params.items() 
            if k.lower() not in tracking_params
        }
        
        # Rebuild query string
        clean_query = urlencode(filtered_params, doseq=True) if filtered_params else ''
        
        # Clean up path
        path = parsed.path.rstrip('/') if parsed.path != '/' else '/'
        
        # Rebuild URL
        normalized = urlunparse((
            scheme,
            parsed.netloc,
            path,
            parsed.params,
            clean_query,
            ''  # Remove fragment
        ))
        
        return normalized
        
    except Exception:
        # If parsing fails, return lowercase stripped version
        return url.lower().strip()


def extract_domain(url: str) -> str:
    """
    Extract domain from URL
    
    Args:
        url: URL string
        
    Returns:
        Domain string (without www prefix)
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    except:
        return ""


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid and well-formed
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return all([
            parsed.scheme in ('http', 'https'),
            parsed.netloc,
            '.' in parsed.netloc,  # Has domain extension
            not parsed.netloc.startswith('.'),  # Doesn't start with dot
            not parsed.netloc.endswith('.')   # Doesn't end with dot
        ])
    except:
        return False


def url_to_filename(url: str) -> str:
    """
    Convert URL to safe filename for caching/storage
    
    Args:
        url: URL string
        
    Returns:
        Safe filename string
    """
    # Use hash of normalized URL
    normalized = normalize_url(url)
    url_hash = hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    # Extract domain for readability
    domain = extract_domain(url)
    safe_domain = re.sub(r'[^a-zA-Z0-9.-]', '_', domain)
    
    return f"{safe_domain}_{url_hash[:8]}"


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract URLs from text content
    
    Args:
        text: Text content to search
        
    Returns:
        List of found URLs
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    urls = url_pattern.findall(text)
    return [url for url in urls if is_valid_url(url)]


def get_url_depth(url: str) -> int:
    """
    Get URL path depth (number of path segments)
    
    Args:
        url: URL string
        
    Returns:
        Number of path segments
    """
    try:
        parsed = urlparse(url)
        path_parts = [part for part in parsed.path.split('/') if part]
        return len(path_parts)
    except:
        return 0


def urls_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs are from the same domain
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        True if same domain, False otherwise
    """
    domain1 = extract_domain(url1)
    domain2 = extract_domain(url2)
    return domain1 == domain2 and domain1 != ""


def calculate_url_similarity(url1: str, url2: str) -> float:
    """
    Calculate similarity between two URLs (0.0 to 1.0)
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not url1 or not url2:
        return 0.0
    
    # Must be same domain for any meaningful similarity
    if not urls_same_domain(url1, url2):
        return 0.0
    
    try:
        parsed1 = urlparse(normalize_url(url1))
        parsed2 = urlparse(normalize_url(url2))
        
        # Path similarity using Levenshtein-like approach
        path1_parts = [part for part in parsed1.path.split('/') if part]
        path2_parts = [part for part in parsed2.path.split('/') if part]
        
        if not path1_parts and not path2_parts:
            return 1.0  # Both are root paths
        
        if not path1_parts or not path2_parts:
            return 0.3  # One is root, one isn't - some similarity for same domain
        
        # Calculate path similarity
        max_length = max(len(path1_parts), len(path2_parts))
        if max_length == 0:
            return 1.0
        
        matching_parts = 0
        for i in range(min(len(path1_parts), len(path2_parts))):
            if path1_parts[i] == path2_parts[i]:
                matching_parts += 1
            else:
                break  # Stop at first non-matching part
        
        path_similarity = matching_parts / max_length
        
        # Query parameter similarity
        params1 = set(parse_qs(parsed1.query).keys())
        params2 = set(parse_qs(parsed2.query).keys())
        
        if params1 or params2:
            param_intersection = len(params1.intersection(params2))
            param_union = len(params1.union(params2))
            param_similarity = param_intersection / param_union if param_union > 0 else 0
        else:
            param_similarity = 1.0  # Both have no parameters
        
        # Weighted combination (path more important than parameters)
        overall_similarity = (path_similarity * 0.8) + (param_similarity * 0.2)
        
        return overall_similarity
        
    except Exception:
        return 0.0


def is_likely_rss_url(url: str) -> bool:
    """
    Check if URL is likely to be an RSS feed
    
    Args:
        url: URL to check
        
    Returns:
        True if likely RSS feed, False otherwise
    """
    url_lower = url.lower()
    
    # Check for common RSS patterns
    rss_indicators = [
        'rss', 'feed', 'atom', '.xml', 'feeds/',
        '/rss/', '/feed/', '/atom/', 'rss.xml',
        'feed.xml', 'atom.xml', 'index.xml'
    ]
    
    return any(indicator in url_lower for indicator in rss_indicators)


def is_likely_api_url(url: str) -> bool:
    """
    Check if URL is likely to be an API endpoint
    
    Args:
        url: URL to check
        
    Returns:
        True if likely API endpoint, False otherwise
    """
    url_lower = url.lower()
    
    # Check for common API patterns
    api_indicators = [
        '/api/', 'api.', '/v1/', '/v2/', '/v3/',
        'rest.', 'graphql', '.json', '/json/',
        'webhook', '/webhooks/'
    ]
    
    return any(indicator in url_lower for indicator in api_indicators)


def get_url_file_extension(url: str) -> Optional[str]:
    """
    Get file extension from URL path
    
    Args:
        url: URL string
        
    Returns:
        File extension (without dot) or None if no extension
    """
    try:
        parsed = urlparse(url)
        path = parsed.path
        
        if '.' in path:
            extension = path.split('.')[-1].lower()
            # Only return if it looks like a real extension (alphanumeric, 2-5 chars)
            if extension and extension.isalnum() and 2 <= len(extension) <= 5:
                return extension
        
        return None
    except:
        return None


def build_query_url(base_url: str, params: Dict[str, str]) -> str:
    """
    Build URL with query parameters
    
    Args:
        base_url: Base URL string
        params: Dictionary of query parameters
        
    Returns:
        URL with query parameters
    """
    try:
        parsed = urlparse(base_url)
        
        # Merge existing params with new ones
        existing_params = parse_qs(parsed.query)
        for key, value in params.items():
            existing_params[key] = [value]
        
        # Rebuild query string
        query = urlencode(existing_params, doseq=True)
        
        # Rebuild URL
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            query,
            parsed.fragment
        ))
        
    except Exception:
        # Fallback: simple concatenation
        separator = '&' if '?' in base_url else '?'
        param_string = urlencode(params)
        return f"{base_url}{separator}{param_string}"


def validate_sample_urls(urls: List[str], base_domain: Optional[str] = None) -> Tuple[List[str], List[str]]:
    """
    Validate list of sample URLs
    
    Args:
        urls: List of URLs to validate
        base_domain: Optional base domain to check against
        
    Returns:
        Tuple of (valid_urls, invalid_urls)
    """
    valid_urls = []
    invalid_urls = []
    
    for url in urls:
        if not url or not isinstance(url, str):
            invalid_urls.append(url)
            continue
        
        url = url.strip()
        
        if not is_valid_url(url):
            invalid_urls.append(url)
            continue
        
        # Check domain matching if base_domain provided
        if base_domain and not urls_same_domain(url, f"https://{base_domain}"):
            invalid_urls.append(url)
            continue
        
        valid_urls.append(url)
    
    return valid_urls, invalid_urls


# URL patterns for common source types
SOURCE_TYPE_PATTERNS = {
    'rss_feed': [
        r'.*/(rss|feed|atom)/?$',
        r'.*\.(xml|rss|atom)$',
        r'.*/feeds?/',
        r'.*/(rss|feed|atom)\.',
    ],
    'newsletter': [
        r'.*/newsletter',
        r'.*/subscribe',
        r'.*/signup',
        r'.*/mailing',
        r'.*/updates',
    ],
    'api': [
        r'.*/api/',
        r'api\.',
        r'.*/v[0-9]+/',
        r'.*/rest/',
        r'.*/graphql',
    ],
    'pdf': [
        r'.*\.pdf$',
    ],
    'social_media': [
        r'.*twitter\.com/',
        r'.*x\.com/',
        r'.*linkedin\.com/',
        r'.*facebook\.com/',
        r'.*instagram\.com/',
    ]
}


def classify_url_by_pattern(url: str) -> Optional[str]:
    """
    Classify URL by pattern matching
    
    Args:
        url: URL to classify
        
    Returns:
        Source type string or None if no match
    """
    url_lower = url.lower()
    
    for source_type, patterns in SOURCE_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url_lower):
                return source_type
    
    return None
