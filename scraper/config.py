"""
Configuration management — load and validate scraping job definitions.

Jobs are defined in a YAML file (jobs.yaml) and loaded into
Python objects for the scheduler and scraper to use.
"""

import yaml
import os
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


@dataclass
class JobConfig:
    """Configuration for a single scraping job."""
    
    name: str
    url: str
    selector: str
    extract: str = "text"
    interval_minutes: int = 60
    notify: List[str] = field(default_factory=lambda: ["console"])
    on_change: bool = True
    max_items: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    
    def validate(self):
        """
        Validate job configuration.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if not self.name:
            errors.append("Job name is required")
        if not self.url:
            errors.append(f"URL is required for job '{self.name}'")
        if not self.selector:
            errors.append(f"Selector is required for job '{self.name}'")
        if self.extract not in ["text", "html", "href", "src"]:
            errors.append(f"Invalid extract type '{self.extract}' for job '{self.name}'")
        if self.interval_minutes < 1:
            errors.append(f"Interval must be at least 1 minute for job '{self.name}'")
        
        valid_channels = ["email", "telegram", "console"]
        for channel in self.notify:
            if channel not in valid_channels:
                errors.append(f"Invalid notify channel '{channel}' for job '{self.name}'")
        
        return errors


def load_jobs(config_path="jobs.yaml"):
    """
    Load job configurations from a YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        List of JobConfig objects
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If configuration is invalid
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    
    if not raw or "jobs" not in raw:
        raise ValueError("Configuration must contain a 'jobs' key")
    
    jobs = []
    all_errors = []
    
    for job_data in raw["jobs"]:
        job = JobConfig(**job_data)
        errors = job.validate()
        
        if errors:
            all_errors.extend(errors)
        else:
            jobs.append(job)
            logger.info(f"Loaded job: {job.name}")
    
    if all_errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in all_errors))
    
    logger.info(f"Loaded {len(jobs)} scraping jobs")
    return jobs


def get_job_by_name(jobs, name):
    """
    Find a job by name (case-insensitive).
    
    Args:
        jobs: List of JobConfig objects
        name: Job name to search for
        
    Returns:
        JobConfig or None
    """
    for job in jobs:
        if job.name.lower() == name.lower():
            return job
    return None
