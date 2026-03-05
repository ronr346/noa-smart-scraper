"""
Job scheduler — run scraping jobs at configured intervals.

Uses APScheduler to manage periodic scraping tasks.
Each job runs independently with its own interval.
"""

import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from scraper.core import Scraper
from scraper.parser import HTMLParser
from scraper.notifier import Notifier
from scraper.storage import Storage

logger = logging.getLogger(__name__)


class ScraperScheduler:
    """
    Schedule and execute scraping jobs.
    
    Usage:
        scheduler = ScraperScheduler(jobs)
        scheduler.start()  # Blocks until interrupted
    """
    
    def __init__(self, jobs, output_dir="output"):
        """
        Initialize scheduler with job configurations.
        
        Args:
            jobs: List of JobConfig objects
            output_dir: Directory for saving scraped data
        """
        self.jobs = jobs
        self.scraper = Scraper()
        self.notifier = Notifier()
        self.storage = Storage(output_dir)
        self.scheduler = BlockingScheduler()
    
    def start(self):
        """
        Start the scheduler — runs until interrupted (Ctrl+C).
        
        Adds all configured jobs and begins execution.
        """
        for job in self.jobs:
            self.scheduler.add_job(
                self._run_job,
                "interval",
                minutes=job.interval_minutes,
                args=[job],
                id=job.name,
                next_run_time=datetime.now(),  # Run immediately on start
            )
            logger.info(f"Scheduled '{job.name}' every {job.interval_minutes} minutes")
        
        logger.info(f"Starting scheduler with {len(self.jobs)} jobs...")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.scraper.close()
    
    def run_once(self, job):
        """
        Run a single job immediately (without scheduling).
        
        Args:
            job: JobConfig object
            
        Returns:
            List of extracted items
        """
        return self._run_job(job)
    
    def _run_job(self, job):
        """
        Execute a single scraping job.
        
        Steps:
        1. Fetch the web page
        2. Parse and extract data
        3. Check for changes
        4. Save data
        5. Send notifications
        
        Args:
            job: JobConfig object
            
        Returns:
            List of extracted items
        """
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] Running: {job.name}")
        
        try:
            # Step 1: Fetch page
            html = self.scraper.fetch(job.url, headers=job.headers)
            
            # Step 2: Parse and extract
            parser = HTMLParser(html)
            
            if job.extract == "text":
                items = parser.extract_text(job.selector, max_items=job.max_items)
            elif job.extract == "html":
                items = parser.extract_html(job.selector, max_items=job.max_items)
            else:
                items = parser.extract_attribute(job.selector, job.extract, 
                                                  max_items=job.max_items)
            
            logger.info(f"Found {len(items)} items for '{job.name}'")
            
            if not items:
                logger.warning(f"No items found for '{job.name}' — check selector")
                return []
            
            # Step 3: Check for changes
            changed = self.notifier.has_changed(job.name, items)
            
            # Step 4: Save data
            self.storage.save(job.name, items)
            
            # Step 5: Send notifications (if changed or on_change is False)
            if changed or not job.on_change:
                message = self._format_notification(job.name, items)
                self.notifier.send(message, 
                                   subject=f"Scraper Alert: {job.name}",
                                   channels=job.notify)
            
            return items
            
        except Exception as e:
            logger.error(f"Job '{job.name}' failed: {str(e)}")
            self.notifier.send(
                f"⚠️ Scraping job '{job.name}' failed:\n{str(e)}",
                channels=["console"]
            )
            return []
    
    def _format_notification(self, job_name, items):
        """Format items into a readable notification message."""
        header = f"🔔 <b>{job_name}</b>\n"
        header += f"Found {len(items)} items:\n\n"
        
        body = ""
        for i, item in enumerate(items[:10], 1):
            text = str(item)[:100]  # Truncate long items
            body += f"{i}. {text}\n"
        
        if len(items) > 10:
            body += f"\n... and {len(items) - 10} more"
        
        return header + body
