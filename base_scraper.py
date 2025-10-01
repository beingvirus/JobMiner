"""
Base scraper class for JobMiner - provides common functionality for all job site scrapers.
"""

import requests
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dataclasses import dataclass
from datetime import datetime


@dataclass
class JobListing:
    """Data model for a job listing."""
    title: str
    company: str
    location: str
    description: str
    salary: Optional[str] = None
    job_type: Optional[str] = None  # Full-time, Part-time, Contract, etc.
    experience_level: Optional[str] = None
    posted_date: Optional[str] = None
    job_url: Optional[str] = None
    scraped_at: datetime = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert job listing to dictionary."""
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'salary': self.salary,
            'job_type': self.job_type,
            'experience_level': self.experience_level,
            'posted_date': self.posted_date,
            'job_url': self.job_url,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }


class BaseScraper(ABC):
    """Abstract base class for all job site scrapers."""
    
    def __init__(self, delay: float = 1.0, timeout: int = 30):
        """
        Initialize the base scraper.
        
        Args:
            delay: Delay between requests in seconds
            timeout: Request timeout in seconds
        """
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.ua = UserAgent()
        self.logger = self._setup_logger()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the scraper."""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Add delay to be respectful
            time.sleep(self.delay)
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = ' '.join(text.strip().split())
        return cleaned
    
    @abstractmethod
    def get_job_urls(self, search_term: str, location: str = "", max_pages: int = 1) -> List[str]:
        """
        Get list of job URLs for given search criteria.
        
        Args:
            search_term: Job title or keyword to search for
            location: Location to search in
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of job URLs
        """
        pass
    
    @abstractmethod
    def parse_job(self, job_url: str) -> Optional[JobListing]:
        """
        Parse a single job listing from its URL.
        
        Args:
            job_url: URL of the job listing
            
        Returns:
            JobListing object or None if parsing failed
        """
        pass
    
    def scrape_jobs(self, search_term: str, location: str = "", max_pages: int = 1) -> List[JobListing]:
        """
        Main method to scrape jobs for given criteria.
        
        Args:
            search_term: Job title or keyword to search for
            location: Location to search in
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of JobListing objects
        """
        self.logger.info(f"Starting scrape for '{search_term}' in '{location}'")
        
        # Get job URLs
        job_urls = self.get_job_urls(search_term, location, max_pages)
        self.logger.info(f"Found {len(job_urls)} job URLs")
        
        # Parse each job
        jobs = []
        for i, url in enumerate(job_urls, 1):
            self.logger.info(f"Parsing job {i}/{len(job_urls)}")
            job = self.parse_job(url)
            if job:
                jobs.append(job)
        
        self.logger.info(f"Successfully scraped {len(jobs)} jobs")
        return jobs
    
    def save_to_json(self, jobs: List[JobListing], filename: str):
        """Save jobs to JSON file."""
        import json
        
        jobs_data = [job.to_dict() for job in jobs]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Saved {len(jobs)} jobs to {filename}")
    
    def save_to_csv(self, jobs: List[JobListing], filename: str):
        """Save jobs to CSV file."""
        import pandas as pd
        
        jobs_data = [job.to_dict() for job in jobs]
        df = pd.DataFrame(jobs_data)
        df.to_csv(filename, index=False, encoding='utf-8')
        
        self.logger.info(f"Saved {len(jobs)} jobs to {filename}")
