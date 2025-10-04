"""
Demo Company Scraper - A template scraper for JobMiner.

This is a demonstration scraper that shows how to implement the BaseScraper
for a hypothetical job site. It serves as a template for creating real scrapers.
"""

import sys
import os
from typing import List, Optional
from urllib.parse import urljoin, quote

# Add parent directory to path to import base_scraper
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from base_scraper import BaseScraper, JobListing


class DemoCompanyScraper(BaseScraper):
    """
    Demo scraper implementation.
    
    This scraper demonstrates the structure and methods needed
    to create a real job site scraper.
    """
    
    def __init__(self, delay: float = 2.0):
        """Initialize the demo scraper with a longer delay."""
        super().__init__(delay=delay)
        self.base_url = "https://example-job-site.com"
        self.search_url = f"{self.base_url}/jobs/search"
    
    def get_job_urls(self, search_term: str, location: str = "", max_pages: int = 1) -> List[str]:
        """
        Get job URLs from search results.
        
        This is a demo implementation that would normally:
        1. Build search URL with parameters
        2. Fetch search results pages
        3. Extract job URLs from each page
        
        Args:
            search_term: Job title or keyword
            location: Location to search in
            max_pages: Maximum pages to scrape
            
        Returns:
            List of job URLs
        """
        job_urls = []
        
        for page in range(1, max_pages + 1):
            # Build search URL (demo format)
            search_params = {
                'q': search_term,
                'location': location,
                'page': page
            }
            
            # In a real scraper, you would:
            # search_url = f"{self.search_url}?q={quote(search_term)}&location={quote(location)}&page={page}"
            # soup = self.get_page(search_url)
            
            # For demo purposes, we'll create mock URLs
            self.logger.info(f"Demo: Searching page {page} for '{search_term}' in '{location}'")
            
            # Mock job URLs (in real scraper, extract from search results)
            page_urls = [
                f"{self.base_url}/job/demo-{search_term.replace(' ', '-')}-{i + (page-1)*10}"
                for i in range(1, 11)  # 10 jobs per page
            ]
            
            job_urls.extend(page_urls)
            
            # In real scraper, check if there are more pages
            # if not soup.find('a', {'class': 'next-page'}):
            #     break
        
        return job_urls[:min(len(job_urls), max_pages * 10)]  # Limit results
    
    def parse_job(self, job_url: str) -> Optional[JobListing]:
        """
        Parse a single job listing.
        
        This is a demo implementation that would normally:
        1. Fetch the job page
        2. Extract job details using CSS selectors
        3. Clean and structure the data
        
        Args:
            job_url: URL of the job listing
            
        Returns:
            JobListing object or None
        """
        # In a real scraper, you would fetch and parse the page:
        # soup = self.get_page(job_url)
        # if not soup:
        #     return None
        
        # For demo purposes, create a mock job listing
        self.logger.info(f"Demo: Parsing job from {job_url}")
        
        # Extract job ID from URL for demo data
        job_id = job_url.split('/')[-1]
        
        # Mock job data (in real scraper, extract from HTML)
        job = JobListing(
            title=f"Demo {job_id.replace('-', ' ').title()}",
            company="Demo Company Inc.",
            location="Remote / San Francisco, CA",
            description=f"This is a demo job listing for {job_id}. "
                       f"In a real scraper, this would be extracted from the job page HTML. "
                       f"The description would include job requirements, responsibilities, "
                       f"and other relevant details.",
            salary="$80,000 - $120,000",
            job_type="Full-time",
            experience_level="Mid-level",
            posted_date="2 days ago",
            job_url=job_url
        )
        
        # In a real scraper, you would extract data like this:
        # job = JobListing(
        #     title=self.clean_text(soup.find('h1', {'class': 'job-title'}).text),
        #     company=self.clean_text(soup.find('div', {'class': 'company-name'}).text),
        #     location=self.clean_text(soup.find('div', {'class': 'job-location'}).text),
        #     description=self.clean_text(soup.find('div', {'class': 'job-description'}).text),
        #     salary=self.clean_text(soup.find('span', {'class': 'salary'}).text) if soup.find('span', {'class': 'salary'}) else None,
        #     job_type=self.clean_text(soup.find('span', {'class': 'job-type'}).text) if soup.find('span', {'class': 'job-type'}) else None,
        #     experience_level=self.clean_text(soup.find('span', {'class': 'experience'}).text) if soup.find('span', {'class': 'experience'}) else None,
        #     posted_date=self.clean_text(soup.find('time', {'class': 'posted-date'}).text) if soup.find('time', {'class': 'posted-date'}) else None,
        #     job_url=job_url
        # )
        
        return job


def main():
    """Demo script to test the scraper."""
    scraper = DemoCompanyScraper()
    
    # Test scraping
    jobs = scraper.scrape_jobs(
        search_term="python developer",
        location="san francisco",
        max_pages=2
    )
    
    # Save results
    scraper.save_to_json(jobs, "demo_jobs.json")
    scraper.save_to_csv(jobs, "demo_jobs.csv")
    
    print(f"\nDemo scraping completed!")
    print(f"Found {len(jobs)} jobs")
    print(f"Results saved to demo_jobs.json and demo_jobs.csv")
    
    # Print first job as example
    if jobs:
        print(f"\nExample job:")
        print(f"Title: {jobs[0].title}")
        print(f"Company: {jobs[0].company}")
        print(f"Location: {jobs[0].location}")
        print(f"Salary: {jobs[0].salary}")


if __name__ == "__main__":
    main()
