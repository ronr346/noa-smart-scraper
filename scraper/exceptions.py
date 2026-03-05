"""
Custom exceptions for the Smart Scraper.

Provides specific error types for better error handling
and clearer error messages in logs and notifications.
"""


class ScraperError(Exception):
    """Base exception for all scraper errors."""
    pass


class FetchError(ScraperError):
    """Raised when a page cannot be fetched."""
    def __init__(self, url, reason="Unknown"):
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to fetch {url}: {reason}")


class ParseError(ScraperError):
    """Raised when HTML content cannot be parsed."""
    def __init__(self, selector, reason="No elements found"):
        self.selector = selector
        self.reason = reason
        super().__init__(f"Parse error for '{selector}': {reason}")


class ConfigError(ScraperError):
    """Raised when job configuration is invalid."""
    pass


class NotificationError(ScraperError):
    """Raised when a notification fails to send."""
    def __init__(self, channel, reason="Unknown"):
        self.channel = channel
        self.reason = reason
        super().__init__(f"Notification via {channel} failed: {reason}")
