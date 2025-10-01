#!/usr/bin/env python3
"""
Batch scraping example for JobMiner.

This script demonstrates how to scrape multiple job searches
in batch and combine the results.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scrapers.demo_company.demo_company import DemoCompanyScraper


def main():
    """Batch scraping example."""
    print("JobMiner Batch Scraping Example")
    print("=" * 35)
    
    # Define multiple search queries
    search_queries = [
        {"term": "python developer", "location": "san francisco"},
        {"term": "data scientist", "location": "new york"},
        {"term": "machine learning engineer", "location": "seattle"},
        {"term": "software engineer", "location": "austin"},
        {"term": "devops engineer", "location": "remote"},
    ]
    
    # Initialize scraper
    scraper = DemoCompanyScraper(delay=0.5)
    
    all_jobs = []
    
    print(f"Starting batch scraping for {len(search_queries)} queries...")
    print()
    
    # Process each query
    for i, query in enumerate(search_queries, 1):
        print(f"Query {i}/{len(search_queries)}: '{query['term']}' in '{query['location']}'")
        
        try:
            jobs = scraper.scrape_jobs(
                search_term=query['term'],
                location=query['location'],
                max_pages=1
            )
            
            print(f"  ✓ Found {len(jobs)} jobs")
            all_jobs.extend(jobs)
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nBatch scraping completed!")
    print(f"Total jobs collected: {len(all_jobs)}")
    
    if all_jobs:
        # Save combined results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"examples/batch_jobs_{timestamp}.json"
        csv_file = f"examples/batch_jobs_{timestamp}.csv"
        
        scraper.save_to_json(all_jobs, json_file)
        scraper.save_to_csv(all_jobs, csv_file)
        
        print(f"\nResults saved:")
        print(f"  JSON: {json_file}")
        print(f"  CSV: {csv_file}")
        
        # Analyze results
        print(f"\nJob Analysis:")
        
        # Count by location
        locations = {}
        job_types = {}
        companies = {}
        
        for job in all_jobs:
            # Count locations
            loc = job.location
            locations[loc] = locations.get(loc, 0) + 1
            
            # Count job types
            jtype = job.job_type or "Unknown"
            job_types[jtype] = job_types.get(jtype, 0) + 1
            
            # Count companies
            comp = job.company
            companies[comp] = companies.get(comp, 0) + 1
        
        print(f"  Locations: {dict(sorted(locations.items(), key=lambda x: x[1], reverse=True))}")
        print(f"  Job Types: {dict(sorted(job_types.items(), key=lambda x: x[1], reverse=True))}")
        print(f"  Companies: {dict(sorted(companies.items(), key=lambda x: x[1], reverse=True))}")
        
        # Show sample jobs
        print(f"\nSample Jobs:")
        for i, job in enumerate(all_jobs[:3], 1):
            print(f"\n  Job {i}:")
            print(f"    Title: {job.title}")
            print(f"    Company: {job.company}")
            print(f"    Location: {job.location}")
            print(f"    Salary: {job.salary}")


if __name__ == "__main__":
    main()
