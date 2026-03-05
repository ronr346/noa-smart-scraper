"""Tests for the HTML parser module."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scraper.parser import HTMLParser


SAMPLE_HTML = """
<html>
<body>
    <div class="articles">
        <div class="article">
            <h2 class="title">First Article</h2>
            <p class="summary">Summary of first article</p>
            <a href="/article/1" class="link">Read more</a>
            <span class="price">$19.99</span>
        </div>
        <div class="article">
            <h2 class="title">Second Article</h2>
            <p class="summary">Summary of second article</p>
            <a href="/article/2" class="link">Read more</a>
            <span class="price">$29.99</span>
        </div>
        <div class="article">
            <h2 class="title">Third Article</h2>
            <p class="summary">Summary of third article</p>
            <a href="/article/3" class="link">Read more</a>
            <span class="price">$39.99</span>
        </div>
    </div>
    <table id="data-table">
        <thead>
            <tr><th>Name</th><th>Value</th></tr>
        </thead>
        <tbody>
            <tr><td>Alpha</td><td>100</td></tr>
            <tr><td>Beta</td><td>200</td></tr>
        </tbody>
    </table>
</body>
</html>
"""


class TestExtractText:
    """Test text extraction."""
    
    def test_extract_all_titles(self):
        """Extracts text from all matching elements."""
        parser = HTMLParser(SAMPLE_HTML)
        titles = parser.extract_text(".title")
        
        assert len(titles) == 3
        assert titles[0] == "First Article"
        assert titles[2] == "Third Article"
    
    def test_extract_with_max_items(self):
        """Respects max_items limit."""
        parser = HTMLParser(SAMPLE_HTML)
        titles = parser.extract_text(".title", max_items=2)
        
        assert len(titles) == 2
    
    def test_extract_no_match(self):
        """Returns empty list when selector doesn't match."""
        parser = HTMLParser(SAMPLE_HTML)
        result = parser.extract_text(".nonexistent")
        
        assert result == []


class TestExtractAttribute:
    """Test attribute extraction."""
    
    def test_extract_href(self):
        """Extracts href attributes from links."""
        parser = HTMLParser(SAMPLE_HTML)
        links = parser.extract_attribute("a.link", "href")
        
        assert len(links) == 3
        assert links[0] == "/article/1"
        assert links[1] == "/article/2"
    
    def test_extract_with_max(self):
        """Respects max_items for attributes."""
        parser = HTMLParser(SAMPLE_HTML)
        links = parser.extract_attribute("a.link", "href", max_items=1)
        
        assert len(links) == 1


class TestExtractTable:
    """Test table extraction."""
    
    def test_extract_table_data(self):
        """Extracts table rows as dictionaries."""
        parser = HTMLParser(SAMPLE_HTML)
        rows = parser.extract_table("#data-table")
        
        assert len(rows) == 2
        assert rows[0]["Name"] == "Alpha"
        assert rows[0]["Value"] == "100"
        assert rows[1]["Name"] == "Beta"
    
    def test_extract_missing_table(self):
        """Returns empty list when table not found."""
        parser = HTMLParser(SAMPLE_HTML)
        rows = parser.extract_table("#nonexistent")
        
        assert rows == []


class TestExtractStructured:
    """Test structured data extraction."""
    
    def test_extract_articles(self):
        """Extracts multiple fields from container elements."""
        parser = HTMLParser(SAMPLE_HTML)
        articles = parser.extract_structured(".article", {
            "title": ".title",
            "summary": ".summary",
            "link": ("a.link", "href"),
            "price": ".price",
        })
        
        assert len(articles) == 3
        assert articles[0]["title"] == "First Article"
        assert articles[0]["link"] == "/article/1"
        assert articles[0]["price"] == "$19.99"


class TestFindText:
    """Test regex text search."""
    
    def test_find_prices(self):
        """Finds text matching a regex pattern."""
        parser = HTMLParser(SAMPLE_HTML)
        prices = parser.find_text(r"\$\d+\.\d+")
        
        assert len(prices) == 3
        assert "$19.99" in prices
