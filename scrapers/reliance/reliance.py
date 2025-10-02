"""
Reliance Scraper for JobMiner.

This scraper extracts job listings from Reliance careers website.
"""

import os
import sys
import time
from typing import List, Optional
from urllib.parse import quote, urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Add parent directory to path to import base_scraper
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from base_scraper import BaseScraper, JobListing

class RelianceScraper(BaseScraper):
    """
    Reliance job scraper using Selenium.
    """
    
    def __init__(self, delay: float = 2.0):
        """Initialize the Reliance scraper."""
        super().__init__(delay=delay)
        self.base_url = "https://careers.ril.com"
        self.search_url = f"{self.base_url}/rilcareers/frmJobSearch.aspx"
        self.driver = None
    
    def _init_driver(self):
        """Initialize Selenium WebDriver."""
        if self.driver is None:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
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
        Get job URLs from Reliance search results.
        """
        driver = self._init_driver()
        job_urls = []
        
        try:
            driver.get(self.search_url)
            
            # Wait for the jobs table to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "MainContent_rgJobs"))
            )
            
            pages_scraped = 0
            while pages_scraped < max_pages:
                # Get job links from current page
                rows = driver.find_elements(By.CSS_SELECTOR, "#MainContent_rgJobs tbody tr")
                
                for row in rows[:-1]:  # Skip last row (pagination)
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 5:
                        try:
                            link_elem = cols[1].find_element(By.TAG_NAME, "a")
                            job_url = link_elem.get_attribute("href")
                            if job_url:
                                job_urls.append(job_url)
                        except:
                            continue
                
                pages_scraped += 1
                
                # Try to go to next page
                if pages_scraped < max_pages:
                    try:
                        next_btn = driver.find_element(By.ID, "MainContent_rgJobs_lnkNext")
                        if "aspNetDisabled" in next_btn.get_attribute("class"):
                            break
                        next_btn.click()
                        time.sleep(self.delay)
                    except:
                        break
            
        except Exception as e:
            self.logger.error(f"Error getting job URLs: {e}")
        
        return job_urls

    def parse_job(self, job_url: str) -> Optional[JobListing]:
        """
        Parse a single job listing from Reliance.
        """
        driver = self._init_driver()
        
        try:
            driver.get(job_url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "contentarea"))
            )
            
            # Extract job details
            title = driver.find_element(By.ID, "MainContent_lblJobTitle").text.strip()
            posted_date = driver.find_element(By.ID, "MainContent_lblPostedDate").text.strip()
            location = driver.find_element(By.ID, "MainContent_lblLoc").text.strip()
            responsibilities = driver.find_element(By.ID, "MainContent_lblSummRole").text.strip()
            education_req = driver.find_element(By.ID, "MainContent_lblEduReq").text.strip()
            experience_req = driver.find_element(By.ID, "MainContent_lblExpReq").text.strip()
            
            # Build description
            description = f"Responsibilities: {responsibilities}\n\nEducation Requirements: {education_req}\n\nExperience Requirements: {experience_req}"
            
            # Extract skills
            skills_list = []
            try:
                skills_table = driver.find_elements(By.CSS_SELECTOR, "table.MsoTableGrid tbody tr")[1:]
                for row in skills_table:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 2:
                        skill_name = cols[0].text.strip()
                        skill_rating = cols[1].text.strip()
                        skills_list.append(f"{skill_name} ({skill_rating})")
            except:
                pass
            
            job = JobListing(
                title=title,
                company="Reliance Industries Limited",
                location=location,
                description=description,
                posted_date=posted_date,
                job_url=job_url,
                experience_level=", ".join(skills_list) if skills_list else None
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
    scraper = RelianceScraper()
    
    jobs = scraper.scrape_jobs(
        search_term="engineer",
        location="mumbai",
        max_pages=1
    )
    
    print(f"Found {len(jobs)} jobs")
    
    if jobs:
        scraper.save_to_json(jobs, "reliance_jobs.json")
        scraper.save_to_csv(jobs, "reliance_jobs.csv")


if __name__ == "__main__":
    main()
