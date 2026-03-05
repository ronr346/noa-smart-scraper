"""
HTML parsing utilities — extract data from web pages using CSS selectors.

The HTMLParser class wraps BeautifulSoup and provides clean methods
for extracting text, attributes, and structured data from HTML.
"""

from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)


class HTMLParser:
    """
    Extract structured data from HTML content.
    
    Usage:
        parser = HTMLParser(html_content)
        titles = parser.extract_text(".article-title")
        links = parser.extract_attribute("a.link", "href")
    """
    
    def __init__(self, html):
        """
        Initialize parser with HTML content.
        
        Args:
            html: HTML string to parse
        """
        self.soup = BeautifulSoup(html, "html.parser")
    
    def extract_text(self, selector, max_items=None):
        """
        Extract text content from elements matching a CSS selector.
        
        Args:
            selector: CSS selector string
            max_items: Maximum number of items to return (None = all)
            
        Returns:
            List of stripped text strings
        """
        elements = self.soup.select(selector)
        
        if max_items:
            elements = elements[:max_items]
        
        results = [el.get_text(strip=True) for el in elements]
        logger.info(f"Extracted {len(results)} text items from '{selector}'")
        return results
    
    def extract_attribute(self, selector, attribute, max_items=None):
        """
        Extract a specific attribute from matching elements.
        
        Args:
            selector: CSS selector string
            attribute: HTML attribute to extract (e.g., 'href', 'src')
            max_items: Maximum number of items to return
            
        Returns:
            List of attribute values
        """
        elements = self.soup.select(selector)
        
        if max_items:
            elements = elements[:max_items]
        
        results = [el.get(attribute) for el in elements if el.get(attribute)]
        logger.info(f"Extracted {len(results)} '{attribute}' values from '{selector}'")
        return results
    
    def extract_html(self, selector, max_items=None):
        """
        Extract inner HTML from matching elements.
        
        Args:
            selector: CSS selector string
            max_items: Maximum number of items
            
        Returns:
            List of HTML strings
        """
        elements = self.soup.select(selector)
        
        if max_items:
            elements = elements[:max_items]
        
        return [str(el) for el in elements]
    
    def extract_table(self, selector="table"):
        """
        Extract data from an HTML table.
        
        Args:
            selector: CSS selector for the table element
            
        Returns:
            List of dictionaries (each row as dict with column headers as keys)
        """
        table = self.soup.select_one(selector)
        if not table:
            logger.warning(f"No table found with selector '{selector}'")
            return []
        
        # Get headers
        headers = []
        header_row = table.select_one("thead tr") or table.select_one("tr")
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.select("th, td")]
        
        # Get data rows
        rows = []
        data_rows = table.select("tbody tr") or table.select("tr")[1:]
        
        for row in data_rows:
            cells = [td.get_text(strip=True) for td in row.select("td")]
            if cells and headers:
                rows.append(dict(zip(headers, cells)))
            elif cells:
                rows.append({f"col_{i}": cell for i, cell in enumerate(cells)})
        
        logger.info(f"Extracted {len(rows)} rows from table")
        return rows
    
    def extract_structured(self, selector, fields):
        """
        Extract structured data — multiple fields from each matching element.
        
        Args:
            selector: CSS selector for container elements
            fields: Dictionary mapping field names to sub-selectors
                     e.g., {"title": "h2", "price": ".price", "link": ("a", "href")}
            
        Returns:
            List of dictionaries with extracted fields
        """
        containers = self.soup.select(selector)
        results = []
        
        for container in containers:
            item = {}
            for field_name, field_selector in fields.items():
                if isinstance(field_selector, tuple):
                    # Tuple means (selector, attribute)
                    sel, attr = field_selector
                    el = container.select_one(sel)
                    item[field_name] = el.get(attr) if el else None
                else:
                    el = container.select_one(field_selector)
                    item[field_name] = el.get_text(strip=True) if el else None
            results.append(item)
        
        logger.info(f"Extracted {len(results)} structured items from '{selector}'")
        return results
    
    def find_text(self, pattern):
        """
        Search for text matching a regex pattern in the entire page.
        
        Args:
            pattern: Regular expression pattern
            
        Returns:
            List of matching strings
        """
        text = self.soup.get_text()
        return re.findall(pattern, text)
