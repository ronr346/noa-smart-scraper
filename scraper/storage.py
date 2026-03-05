"""
Data storage — save scraped data to CSV files.

Handles file creation, appending, and organizing output
by date and job name.
"""

import csv
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Storage:
    """
    Persist scraped data to CSV files.
    
    Usage:
        storage = Storage(output_dir="output")
        storage.save("Tech News", ["Title 1", "Title 2"])
    """
    
    def __init__(self, output_dir="output"):
        """
        Initialize storage with an output directory.
        
        Args:
            output_dir: Directory for CSV output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save(self, job_name, data, timestamp=None):
        """
        Save scraped data to a CSV file.
        
        Files are named: {job_name}_{date}.csv
        New data is appended if the file already exists.
        
        Args:
            job_name: Name of the scraping job
            data: List of items (strings or dictionaries)
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            Path to the saved file
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Create filename from job name and date
        safe_name = job_name.lower().replace(" ", "_")
        date_str = timestamp.strftime("%Y-%m-%d")
        filename = f"{safe_name}_{date_str}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        file_exists = os.path.exists(filepath)
        
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            if isinstance(data[0], dict):
                # Data is list of dictionaries
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerows(data)
            else:
                # Data is list of strings
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["timestamp", "value"])
                for item in data:
                    writer.writerow([timestamp.isoformat(), item])
        
        logger.info(f"Saved {len(data)} items to {filepath}")
        return filepath
    
    def load(self, job_name, date=None):
        """
        Load previously saved data for a job.
        
        Args:
            job_name: Name of the scraping job
            date: Date string (YYYY-MM-DD). Default: today
            
        Returns:
            List of dictionaries (rows from CSV)
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        safe_name = job_name.lower().replace(" ", "_")
        filepath = os.path.join(self.output_dir, f"{safe_name}_{date}.csv")
        
        if not os.path.exists(filepath):
            logger.warning(f"No data file found: {filepath}")
            return []
        
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def get_history(self, job_name):
        """
        List all data files for a specific job.
        
        Args:
            job_name: Name of the scraping job
            
        Returns:
            List of file paths sorted by date
        """
        safe_name = job_name.lower().replace(" ", "_")
        files = [
            f for f in os.listdir(self.output_dir)
            if f.startswith(safe_name) and f.endswith(".csv")
        ]
        return sorted(files)
