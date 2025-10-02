"""
RemoteOK Scraper for JobMiner.

This scraper extracts job listings from RemoteOK.io.
"""

import os
import sys
import time
from typing import List, Optional
from urllib.parse import quote, urljoin

from bs4 import BeautifulSoup
from selenium import webdriver

# Add parent directory to path to import base_scraper
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from base_scraper import BaseScraper, JobListing


class RemoteokCompanyScraper(BaseScraper):
    """
    RemoteOK job scraper using Selenium.
    """
    
    def __init__(self, delay: float = 2.0):
        """Initialize the RemoteOK scraper."""
        super().__init__(delay=delay)
        self.base_url = "https://remoteok.io"
        self.search_url = f"{self.base_url}/remote-jobs"
        self.driver = None
    
    def _init_driver(self):
        """Initialize Selenium WebDriver."""
        if self.driver is None:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=options)
        return self.driver
    
    def _close_driver(self):
        """Close Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def get_job_urls(self, search_term: str, location: str = "", max_pages: int = 1) -> List[str]:
        """
        Get job URLs from RemoteOK search results.
        """
        driver = self._init_driver()
        job_urls = []
        
        try:
            # Build search URL
            search_url = f"{self.base_url}/remote-{search_term.replace(' ', '+')}-jobs"
            
            driver.get(search_url)
            time.sleep(self.delay)
            
            # Get page source and parse with BeautifulSoup
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            # Find all job listings
            job_elements = soup.find_all("tr", class_="job")
            
            for job in job_elements:
                link = job.get("data-href")
                if link:
                    full_url = urljoin(self.base_url, link)
                    job_urls.append(full_url)
            
        except Exception as e:
            self.logger.error(f"Error getting job URLs: {e}")
        
        return job_urls
    
    def parse_job(self, job_url: str) -> Optional[JobListing]:
        """
        Parse a single job listing from RemoteOK.
        """
        driver = self._init_driver()
        
        try:
            driver.get(job_url)
            time.sleep(self.delay)
            
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract job details
            title_elem = soup.find("h1")
            title = self.clean_text(title_elem.text) if title_elem else "N/A"
            
            company_elem = soup.find("h2")
            company = self.clean_text(company_elem.text) if company_elem else "N/A"
            
            # Extract description
            description_elem = soup.find("div", class_="description")
            description = ""
            if description_elem:
                description = self.clean_text(description_elem.get_text(separator='\n'))
            
            # Extract salary if available
            salary_elem = soup.find("td", string="💰")
            salary = None
            if salary_elem and salary_elem.find_next_sibling("td"):
                salary = self.clean_text(salary_elem.find_next_sibling("td").text)
            
            # Extract location (should be Remote)
            location = "Remote"
            
            # Extract job type
            job_type_elem = soup.find("td", string="⏰")
            job_type = None
            if job_type_elem and job_type_elem.find_next_sibling("td"):
                job_type = self.clean_text(job_type_elem.find_next_sibling("td").text)
            
            job = JobListing(
                title=title,
                company=company,
                location=location,
                description=description,
                salary=salary,
                job_type=job_type,
                job_url=job_url
            )
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error parsing job {job_url}: {e}")
            return None
    
    def scrape_jobs(self, search_term: str, location: str = "", max_pages: int = 1) -> List[JobListing]:
        """Override to ensure driver cleanup."""
        try:
            jobs = super().scrape_jobs(search_term, location, max_pages)
            return jobs
        finally:
            self._close_driver()


def main():
    """Test the scraper."""
    scraper = RemoteokCompanyScraper()
    
    jobs = scraper.scrape_jobs(
        search_term="python developer",
        location="remote",
        max_pages=1
    )
    
    print(f"Found {len(jobs)} jobs")
    
    if jobs:
        scraper.save_to_json(jobs, "remoteok_jobs.json")
        scraper.save_to_csv(jobs, "remoteok_jobs.csv")


if __name__ == "__main__":
    main()
