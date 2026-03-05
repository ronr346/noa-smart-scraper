"""Smart Scraper & Notifier — Web scraping with automated notifications."""

from scraper.core import Scraper
from scraper.parser import HTMLParser
from scraper.notifier import Notifier
from scraper.scheduler import ScraperScheduler

__all__ = ["Scraper", "HTMLParser", "Notifier", "ScraperScheduler"]
