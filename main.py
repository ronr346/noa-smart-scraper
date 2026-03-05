"""
Smart Scraper & Notifier — CLI Entry Point

Usage:
    python main.py scrape --job "Job Name"    Run a single job
    python main.py monitor                     Start continuous monitoring
    python main.py list                        List all configured jobs

Examples:
    python main.py scrape --job "Tech News Monitor"
    python main.py monitor
"""

import argparse
import logging
import sys
from scraper.config import load_jobs, get_job_by_name
from scraper.scheduler import ScraperScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def cmd_scrape(args):
    """Run a single scraping job."""
    jobs = load_jobs(args.config)
    job = get_job_by_name(jobs, args.job)
    
    if not job:
        print(f"❌ Job not found: '{args.job}'")
        print(f"Available jobs: {', '.join(j.name for j in jobs)}")
        sys.exit(1)
    
    scheduler = ScraperScheduler([job])
    items = scheduler.run_once(job)
    
    print(f"\n✅ Done! Found {len(items)} items.")
    for i, item in enumerate(items[:10], 1):
        print(f"  {i}. {item[:80]}")
    
    if len(items) > 10:
        print(f"  ... and {len(items) - 10} more")


def cmd_monitor(args):
    """Start continuous monitoring with scheduler."""
    jobs = load_jobs(args.config)
    
    print(f"🚀 Starting monitor with {len(jobs)} jobs:")
    for job in jobs:
        print(f"  • {job.name} — every {job.interval_minutes}min")
    print()
    
    scheduler = ScraperScheduler(jobs)
    scheduler.start()


def cmd_list(args):
    """List all configured jobs."""
    jobs = load_jobs(args.config)
    
    print(f"\n📋 Configured Jobs ({len(jobs)}):\n")
    for job in jobs:
        print(f"  📌 {job.name}")
        print(f"     URL: {job.url}")
        print(f"     Selector: {job.selector}")
        print(f"     Interval: every {job.interval_minutes} minutes")
        print(f"     Notify via: {', '.join(job.notify)}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Smart Scraper & Notifier — Automated web scraping tool"
    )
    parser.add_argument("--config", default="jobs.yaml",
                        help="Path to jobs configuration file")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Run a single scraping job")
    scrape_parser.add_argument("--job", required=True, help="Job name to run")
    
    # Monitor command
    subparsers.add_parser("monitor", help="Start continuous monitoring")
    
    # List command
    subparsers.add_parser("list", help="List all configured jobs")
    
    args = parser.parse_args()
    
    if args.command == "scrape":
        cmd_scrape(args)
    elif args.command == "monitor":
        cmd_monitor(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
