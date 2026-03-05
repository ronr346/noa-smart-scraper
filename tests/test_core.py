"""Tests for the Scraper core module."""

import pytest
import responses
import requests
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scraper.core import Scraper


class TestScraper:
    """Test the HTTP scraper."""
    
    @responses.activate
    def test_fetch_success(self):
        """Successfully fetches a web page."""
        responses.add(
            responses.GET,
            "https://example.com",
            body="<html><body>Hello</body></html>",
            status=200,
        )
        
        scraper = Scraper(delay_between_requests=0)
        html = scraper.fetch("https://example.com")
        
        assert "Hello" in html
        scraper.close()
    
    @responses.activate
    def test_fetch_404(self):
        """Raises exception on 404."""
        responses.add(
            responses.GET,
            "https://example.com/missing",
            status=404,
        )
        
        scraper = Scraper(delay_between_requests=0, max_retries=0)
        
        with pytest.raises(requests.exceptions.HTTPError):
            scraper.fetch("https://example.com/missing")
        
        scraper.close()
    
    @responses.activate
    def test_fetch_timeout(self):
        """Handles timeout gracefully."""
        responses.add(
            responses.GET,
            "https://example.com/slow",
            body=requests.exceptions.Timeout(),
        )
        
        scraper = Scraper(timeout=1, delay_between_requests=0, max_retries=0)
        
        with pytest.raises(requests.exceptions.Timeout):
            scraper.fetch("https://example.com/slow")
        
        scraper.close()
    
    @responses.activate
    def test_fetch_multiple(self):
        """Fetches multiple URLs and returns results dict."""
        responses.add(responses.GET, "https://a.com", body="Page A", status=200)
        responses.add(responses.GET, "https://b.com", body="Page B", status=200)
        
        scraper = Scraper(delay_between_requests=0)
        results = scraper.fetch_multiple(["https://a.com", "https://b.com"])
        
        assert "Page A" in results["https://a.com"]
        assert "Page B" in results["https://b.com"]
        scraper.close()
    
    @responses.activate
    def test_fetch_multiple_partial_failure(self):
        """Handles partial failure in multi-fetch."""
        responses.add(responses.GET, "https://good.com", body="OK", status=200)
        responses.add(responses.GET, "https://bad.com", status=500)
        
        scraper = Scraper(delay_between_requests=0, max_retries=0)
        results = scraper.fetch_multiple(["https://good.com", "https://bad.com"])
        
        assert results["https://good.com"] is not None
        assert results["https://bad.com"] is None
        scraper.close()
    
    def test_context_manager(self):
        """Works as a context manager."""
        with Scraper() as scraper:
            assert scraper.session is not None


class TestRateLimiting:
    """Test rate limiting behavior."""
    
    @responses.activate
    def test_respects_delay(self):
        """Delay is enforced between requests."""
        import time
        
        responses.add(responses.GET, "https://a.com", body="A", status=200)
        responses.add(responses.GET, "https://b.com", body="B", status=200)
        
        scraper = Scraper(delay_between_requests=0.5)
        
        start = time.time()
        scraper.fetch("https://a.com")
        scraper.fetch("https://b.com")
        elapsed = time.time() - start
        
        assert elapsed >= 0.4  # Should have waited ~0.5s
        scraper.close()
