#!/usr/bin/env python3
"""
Database usage example for JobMiner.

This script demonstrates how to use JobMiner with database integration
to store and query job listings.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scrapers.demo_company.demo_company import DemoCompanyScraper
from database import DatabaseManager
from config import get_config


def main():
    """Database usage example."""
    print("JobMiner Database Usage Example")
    print("=" * 35)
    
    # Enable database in config
    config = get_config()
    config.database.enabled = True
    config.database.url = "sqlite:///examples/jobminer_example.db"
    
    # Initialize database manager
    print("1. Initializing database...")
    db_manager = DatabaseManager(config.database.url)
    
    # Initialize scraper
    print("2. Initializing scraper...")
    scraper = DemoCompanyScraper(delay=0.5)
    
    # Scrape some jobs
    print("3. Scraping jobs...")
    jobs1 = scraper.scrape_jobs("python developer", "san francisco", 1)
    jobs2 = scraper.scrape_jobs("data scientist", "new york", 1)
    
    all_jobs = jobs1 + jobs2
    print(f"   Found {len(all_jobs)} total jobs")
    
    # Save to database
    print("4. Saving jobs to database...")
    saved_count = db_manager.save_jobs(all_jobs, "demo-company")
    print(f"   Saved {saved_count} new jobs")
    
    # Query database
    print("\n5. Querying database...")
    
    # Get all jobs
    all_db_jobs = db_manager.get_jobs(limit=50)
    print(f"   Total jobs in database: {len(all_db_jobs)}")
    
    # Search for specific jobs
    python_jobs = db_manager.search_jobs("python")
    print(f"   Python jobs found: {len(python_jobs)}")
    
    # Get jobs by company
    company_jobs = db_manager.get_jobs(company="Demo Company")
    print(f"   Jobs from Demo Company: {len(company_jobs)}")
    
    # Get statistics
    print("\n6. Database statistics:")
    stats = db_manager.get_job_stats()
    print(f"   Total jobs: {stats['total_jobs']}")
    print(f"   Top companies: {stats['top_companies'][:3]}")
    print(f"   Scraper stats: {stats['scraper_stats']}")
    
    # Display some jobs
    print("\n7. Sample jobs from database:")
    for i, job in enumerate(all_db_jobs[:2], 1):
        print(f"\nJob {i}:")
        print(f"  Title: {job.title}")
        print(f"  Company: {job.company}")
        print(f"  Location: {job.location}")
        print(f"  Scraped: {job.scraped_at}")
    
    print("\nDatabase usage example completed!")
    print(f"Database saved at: examples/jobminer_example.db")


if __name__ == "__main__":
    main()
