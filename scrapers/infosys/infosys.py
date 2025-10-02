"""
Infosys Scraper for JobMiner.

This scraper extracts job listings from Infosys careers website.
"""

import json
import os
import re
import sys
import time
from typing import List, Optional
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup

# Add parent directory to path to import base_scraper
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from base_scraper import BaseScraper, JobListing

class InfosysScraper(BaseScraper):
    """
    Infosys job scraper.
    """
    
    def __init__(self, delay: float = 2.0):
        """Initialize the Infosys scraper."""
        super().__init__(delay=delay)
        self.base_url = "https://digitalcareers.infosys.com"
        self.search_url = f"{self.base_url}/infosys/global-careers"

    def get_job_urls(self, search_term: str, location: str = "", max_pages: int = 1) -> List[str]:
        """
        Get job URLs from Infosys search results.
        """
        job_urls = []
        
        for page in range(1, max_pages + 1):
            # Build search URL
            search_url = f"{self.search_url}?location={quote(location)}&keyword={quote(search_term)}"
            if page > 1:
                search_url += f"&page={page}"
            
            soup = self.get_page(search_url)
            if not soup:
                break
            
            # Extract job URLs from search results
            job_links = soup.select("a.job")
            page_urls = []
            
            for link in job_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    page_urls.append(full_url)
            
            job_urls.extend(page_urls)
            
            # Check for next page
            next_link = soup.select_one('a.pagination-button.right[rel="next"]')
            if not next_link or not next_link.get("href"):
                break
        
        return job_urls
    
    def parse_job(self, job_url: str) -> Optional[JobListing]:
        """
        Parse a single job listing from Infosys.
        """
        soup = self.get_page(job_url)
        if not soup:
            return None
        
        try:
            # Extract basic job information
            title_elem = soup.select_one('h1.job-title, .job-title')
            title = self.clean_text(title_elem.text) if title_elem else "N/A"
            
            # Extract location
            location_elem = soup.select_one('#custom_field_work-location')
            location = self.clean_text(location_elem.text) if location_elem else "N/A"
            
            # Extract company
            company_elem = soup.select_one('#custom_field_company')
            company = self.clean_text(company_elem.text) if company_elem else "Infosys"
            
            # Extract job description
            desc_section = soup.select_one('.description-page-right')
            description = ""
            if desc_section:
                description = self.clean_text(desc_section.get_text(separator='\n', strip=True))
                if description.startswith("Job description"):
                    description = description[len("Job description"):].strip()
            
            # Extract skills
            skills_elem = soup.select_one('#custom_field_skillset')
            skills = self.clean_text(skills_elem.text) if skills_elem else None
            
            # Extract domain
            domain_elem = soup.select_one('#custom_field_domain')
            domain = self.clean_text(domain_elem.text) if domain_elem else None
            
            job = JobListing(
                title=title,
                company=company,
                location=location,
                description=description,
                job_url=job_url,
                experience_level=domain,
                job_type=skills
            )
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error parsing job {job_url}: {e}")
            return None


def main():
    """Test the scraper."""
    scraper = InfosysScraper()
    
    jobs = scraper.scrape_jobs(
        search_term="python developer",
        location="bangalore",
        max_pages=1
    )
    
    print(f"Found {len(jobs)} jobs")
    
    if jobs:
        scraper.save_to_json(jobs, "infosys_jobs.json")
        scraper.save_to_csv(jobs, "infosys_jobs.csv")


if __name__ == "__main__":
    main()
