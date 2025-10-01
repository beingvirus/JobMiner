#!/usr/bin/env python3
"""
Basic usage example for JobMiner.

This script demonstrates how to use JobMiner to scrape jobs
and save them in different formats.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the demo scraper
import importlib.util
import os

# Load the demo scraper dynamically
scraper_path = os.path.join(os.path.dirname(__file__), '..', 'scrapers', 'demo-company', 'demo_company.py')
spec = importlib.util.spec_from_file_location("demo_company", scraper_path)
demo_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo_module)
DemoCompanyScraper = demo_module.DemoCompanyScraper


def main():
    """Basic usage example."""
    print("JobMiner Basic Usage Example")
    print("=" * 30)
    
    # Initialize scraper
    print("1. Initializing scraper...")
    scraper = DemoCompanyScraper(delay=1.0)
    
    # Define search parameters
    search_term = "software engineer"
    location = "seattle"
    max_pages = 1
    
    print(f"2. Searching for '{search_term}' in '{location}'...")
    
    # Scrape jobs
    jobs = scraper.scrape_jobs(
        search_term=search_term,
        location=location,
        max_pages=max_pages
    )
    
    print(f"3. Found {len(jobs)} jobs!")
    
    if jobs:
        # Save to different formats
        print("4. Saving results...")
        scraper.save_to_json(jobs, "examples/basic_jobs.json")
        scraper.save_to_csv(jobs, "examples/basic_jobs.csv")
        
        # Display first few jobs
        print("\n5. Sample jobs:")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\nJob {i}:")
            print(f"  Title: {job.title}")
            print(f"  Company: {job.company}")
            print(f"  Location: {job.location}")
            print(f"  Salary: {job.salary}")
            print(f"  Type: {job.job_type}")
    
    print("\nBasic usage example completed!")


if __name__ == "__main__":
    main()
