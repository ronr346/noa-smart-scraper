"""
Core scraper engine — fetches web pages with error handling and retries.

The Scraper class handles HTTP requests with:
- Custom headers and user agents
- Configurable timeouts and retries
- Rate limiting between requests
- Session management for cookie persistence
"""

import time
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class Scraper:
    """
    Web scraper with built-in error handling and rate limiting.
    
    Usage:
        scraper = Scraper()
        html = scraper.fetch("https://example.com")
    """
    
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    def __init__(self, timeout=10, max_retries=3, delay_between_requests=1.0):
        """
        Initialize the scraper.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts on failure
            delay_between_requests: Seconds to wait between requests (rate limiting)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay = delay_between_requests
        self._last_request_time = 0
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update(self.DEFAULT_HEADERS)
    
    def fetch(self, url, headers=None):
        """
        Fetch a web page with error handling and rate limiting.
        
        Args:
            url: URL to fetch
            headers: Optional custom headers (merged with defaults)
            
        Returns:
            HTML content as string
            
        Raises:
            requests.RequestException: If all retries fail
        """
        # Rate limiting — wait if needed
        self._rate_limit()
        
        if headers:
            self.session.headers.update(headers)
        
        logger.info(f"Fetching: {url}")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            logger.info(f"Success: {url} ({response.status_code})")
            return response.text
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: {url}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {url} — {str(e)}")
            raise
    
    def fetch_multiple(self, urls, headers=None):
        """
        Fetch multiple URLs sequentially with rate limiting.
        
        Args:
            urls: List of URLs to fetch
            headers: Optional custom headers
            
        Returns:
            Dictionary mapping URL → HTML content (or None on error)
        """
        results = {}
        
        for url in urls:
            try:
                results[url] = self.fetch(url, headers)
            except requests.RequestException:
                results[url] = None
                logger.warning(f"Skipping failed URL: {url}")
        
        return results
    
    def _rate_limit(self):
        """Enforce delay between requests to be respectful."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay:
            sleep_time = self.delay - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
        self._last_request_time = time.time()
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
