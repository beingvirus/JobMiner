#!/usr/bin/env python3
"""
JobMiner CLI - Command line interface for running job scrapers.
"""

import click
import os
import sys
import importlib.util
import json
from pathlib import Path
from typing import List, Dict, Any


def discover_scrapers() -> Dict[str, str]:
    """
    Discover available scrapers in the scrapers directory.
    
    Returns:
        Dictionary mapping scraper names to their file paths
    """
    scrapers = {}
    scrapers_dir = Path(__file__).parent / "scrapers"
    
    if not scrapers_dir.exists():
        return scrapers
    
    for scraper_dir in scrapers_dir.iterdir():
        if scraper_dir.is_dir():
            # Look for Python files in the scraper directory
            for py_file in scraper_dir.glob("*.py"):
                if not py_file.name.startswith("__"):
                    scraper_name = scraper_dir.name
                    scrapers[scraper_name] = str(py_file)
                    break
    
    return scrapers


def load_scraper_class(scraper_path: str):
    """
    Dynamically load a scraper class from a Python file.
    
    Args:
        scraper_path: Path to the scraper Python file
        
    Returns:
        Scraper class
    """
    spec = importlib.util.spec_from_file_location("scraper_module", scraper_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find the scraper class (should inherit from BaseScraper)
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (isinstance(attr, type) and 
            hasattr(attr, 'scrape_jobs') and 
            attr.__name__ != 'BaseScraper'):
            return attr
    
    raise ValueError(f"No scraper class found in {scraper_path}")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """JobMiner - A Python-based web scraping toolkit for job listings."""
    pass


@cli.command()
def list_scrapers():
    """List all available scrapers."""
    scrapers = discover_scrapers()
    
    if not scrapers:
        click.echo("No scrapers found in the scrapers directory.")
        return
    
    click.echo("Available scrapers:")
    for name, path in scrapers.items():
        click.echo(f"  • {name} ({path})")


@cli.command()
@click.argument('scraper_name')
@click.argument('search_term')
@click.option('--location', '-l', default="", help='Location to search in')
@click.option('--pages', '-p', default=1, help='Number of pages to scrape')
@click.option('--output', '-o', default="jobs", help='Output filename (without extension)')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'both']), 
              default='both', help='Output format')
@click.option('--delay', '-d', default=1.0, help='Delay between requests in seconds')
def scrape(scraper_name, search_term, location, pages, output, format, delay):
    """
    Scrape jobs using a specific scraper.
    
    SCRAPER_NAME: Name of the scraper to use (e.g., 'demo-company')
    SEARCH_TERM: Job title or keyword to search for
    """
    scrapers = discover_scrapers()
    
    if scraper_name not in scrapers:
        click.echo(f"Error: Scraper '{scraper_name}' not found.")
        click.echo("Use 'jobminer list-scrapers' to see available scrapers.")
        return
    
    try:
        # Load the scraper class
        scraper_class = load_scraper_class(scrapers[scraper_name])
        scraper = scraper_class(delay=delay)
        
        click.echo(f"Starting scrape with {scraper_name}...")
        click.echo(f"Search term: {search_term}")
        click.echo(f"Location: {location or 'Any'}")
        click.echo(f"Pages: {pages}")
        click.echo(f"Delay: {delay}s")
        click.echo()
        
        # Scrape jobs
        jobs = scraper.scrape_jobs(search_term, location, pages)
        
        if not jobs:
            click.echo("No jobs found.")
            return
        
        # Save results
        if format in ['json', 'both']:
            json_file = f"{output}.json"
            scraper.save_to_json(jobs, json_file)
            click.echo(f"✓ Saved {len(jobs)} jobs to {json_file}")
        
        if format in ['csv', 'both']:
            csv_file = f"{output}.csv"
            scraper.save_to_csv(jobs, csv_file)
            click.echo(f"✓ Saved {len(jobs)} jobs to {csv_file}")
        
        # Show summary
        click.echo(f"\nScraping completed successfully!")
        click.echo(f"Total jobs found: {len(jobs)}")
        
        # Show sample job
        if jobs:
            click.echo(f"\nSample job:")
            job = jobs[0]
            click.echo(f"  Title: {job.title}")
            click.echo(f"  Company: {job.company}")
            click.echo(f"  Location: {job.location}")
            if job.salary:
                click.echo(f"  Salary: {job.salary}")
        
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('input_file')
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), 
              help='Input file format (auto-detected if not specified)')
def analyze(input_file, format):
    """Analyze scraped job data."""
    if not os.path.exists(input_file):
        click.echo(f"Error: File '{input_file}' not found.")
        return
    
    # Auto-detect format if not specified
    if not format:
        if input_file.endswith('.json'):
            format = 'json'
        elif input_file.endswith('.csv'):
            format = 'csv'
        else:
            click.echo("Error: Cannot detect file format. Please specify with --format")
            return
    
    try:
        if format == 'json':
            with open(input_file, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
        else:  # csv
            import pandas as pd
            df = pd.read_csv(input_file)
            jobs_data = df.to_dict('records')
        
        # Basic analysis
        total_jobs = len(jobs_data)
        click.echo(f"Job Data Analysis for {input_file}")
        click.echo("=" * 40)
        click.echo(f"Total jobs: {total_jobs}")
        
        if total_jobs == 0:
            return
        
        # Company analysis
        companies = {}
        locations = {}
        job_types = {}
        
        for job in jobs_data:
            # Count companies
            company = job.get('company', 'Unknown')
            companies[company] = companies.get(company, 0) + 1
            
            # Count locations
            location = job.get('location', 'Unknown')
            locations[location] = locations.get(location, 0) + 1
            
            # Count job types
            job_type = job.get('job_type', 'Unknown')
            job_types[job_type] = job_types.get(job_type, 0) + 1
        
        # Top companies
        click.echo(f"\nTop 5 Companies:")
        for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]:
            click.echo(f"  {company}: {count} jobs")
        
        # Top locations
        click.echo(f"\nTop 5 Locations:")
        for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]:
            click.echo(f"  {location}: {count} jobs")
        
        # Job types
        click.echo(f"\nJob Types:")
        for job_type, count in sorted(job_types.items(), key=lambda x: x[1], reverse=True):
            click.echo(f"  {job_type}: {count} jobs")
        
    except Exception as e:
        click.echo(f"Error analyzing file: {e}")


@cli.command()
def init():
    """Initialize a new scraper template."""
    click.echo("JobMiner Scraper Template Generator")
    click.echo("=" * 35)
    
    # Get scraper details
    scraper_name = click.prompt("Scraper name (e.g., 'linkedin', 'indeed')")
    company_name = click.prompt("Company/Site name (e.g., 'LinkedIn', 'Indeed')")
    base_url = click.prompt("Base URL (e.g., 'https://linkedin.com')")
    
    # Create directory
    scraper_dir = Path(f"scrapers/{scraper_name}")
    scraper_dir.mkdir(parents=True, exist_ok=True)
    
    # Create scraper file
    scraper_file = scraper_dir / f"{scraper_name.replace('-', '_')}.py"
    
    template_content = f'''"""
{company_name} Scraper for JobMiner.

This scraper extracts job listings from {company_name}.
"""

import sys
import os
from typing import List, Optional
from urllib.parse import urljoin, quote

# Add parent directory to path to import base_scraper
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from base_scraper import BaseScraper, JobListing


class {scraper_name.replace('-', '').title()}Scraper(BaseScraper):
    """
    {company_name} job scraper.
    """
    
    def __init__(self, delay: float = 2.0):
        """Initialize the {company_name} scraper."""
        super().__init__(delay=delay)
        self.base_url = "{base_url}"
        self.search_url = f"{{self.base_url}}/jobs/search"  # Update this URL
    
    def get_job_urls(self, search_term: str, location: str = "", max_pages: int = 1) -> List[str]:
        """
        Get job URLs from {company_name} search results.
        
        TODO: Implement actual search logic
        """
        job_urls = []
        
        for page in range(1, max_pages + 1):
            # TODO: Build actual search URL
            # search_url = f"{{self.search_url}}?q={{quote(search_term)}}&location={{quote(location)}}&page={{page}}"
            
            # TODO: Fetch and parse search results
            # soup = self.get_page(search_url)
            # if not soup:
            #     break
            
            # TODO: Extract job URLs from search results
            # job_links = soup.find_all('a', {{'class': 'job-link-class'}})
            # page_urls = [urljoin(self.base_url, link.get('href')) for link in job_links]
            # job_urls.extend(page_urls)
            
            # TODO: Check for next page
            # if not soup.find('a', {{'class': 'next-page'}}):
            #     break
            
            pass
        
        return job_urls
    
    def parse_job(self, job_url: str) -> Optional[JobListing]:
        """
        Parse a single job listing from {company_name}.
        
        TODO: Implement actual job parsing logic
        """
        soup = self.get_page(job_url)
        if not soup:
            return None
        
        try:
            # TODO: Extract job details using CSS selectors
            # title = self.clean_text(soup.find('h1', {{'class': 'job-title'}}).text)
            # company = self.clean_text(soup.find('div', {{'class': 'company-name'}}).text)
            # location = self.clean_text(soup.find('div', {{'class': 'job-location'}}).text)
            # description = self.clean_text(soup.find('div', {{'class': 'job-description'}}).text)
            
            # TODO: Extract optional fields
            # salary_elem = soup.find('span', {{'class': 'salary'}})
            # salary = self.clean_text(salary_elem.text) if salary_elem else None
            
            # TODO: Create and return JobListing object
            # job = JobListing(
            #     title=title,
            #     company=company,
            #     location=location,
            #     description=description,
            #     salary=salary,
            #     job_url=job_url
            # )
            # return job
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing job {{job_url}}: {{e}}")
            return None


def main():
    """Test the scraper."""
    scraper = {scraper_name.replace('-', '').title()}Scraper()
    
    jobs = scraper.scrape_jobs(
        search_term="python developer",
        location="san francisco",
        max_pages=1
    )
    
    print(f"Found {{len(jobs)}} jobs")
    
    if jobs:
        scraper.save_to_json(jobs, f"{scraper_name}_jobs.json")
        scraper.save_to_csv(jobs, f"{scraper_name}_jobs.csv")


if __name__ == "__main__":
    main()
'''
    
    with open(scraper_file, 'w') as f:
        f.write(template_content)
    
    # Create README
    readme_file = scraper_dir / f"{scraper_name}_readme.md"
    readme_content = f'''# {company_name} Scraper

Scraper for extracting job listings from {company_name}.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Update the scraper implementation in `{scraper_file.name}`

## Usage

```python
from {scraper_name.replace('-', '_')} import {scraper_name.replace('-', '').title()}Scraper

scraper = {scraper_name.replace('-', '').title()}Scraper()
jobs = scraper.scrape_jobs("python developer", "san francisco")
```

## TODO

- [ ] Implement `get_job_urls()` method
- [ ] Implement `parse_job()` method  
- [ ] Add proper CSS selectors for job extraction
- [ ] Handle pagination
- [ ] Add error handling for edge cases
- [ ] Test with various search terms

## Notes

Add any site-specific notes or quirks here.
'''
    
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    # Create requirements.txt
    req_file = scraper_dir / "requirements.txt"
    with open(req_file, 'w') as f:
        f.write("requests==2.31.0\nbeautifulsoup4==4.12.2\npandas==2.1.3\nfake-useragent==1.4.0\nlxml==4.9.3\n")
    
    click.echo(f"\n✓ Created scraper template in {scraper_dir}")
    click.echo(f"✓ Files created:")
    click.echo(f"  - {scraper_file}")
    click.echo(f"  - {readme_file}")
    click.echo(f"  - {req_file}")
    click.echo(f"\nNext steps:")
    click.echo(f"1. Edit {scraper_file} and implement the TODO items")
    click.echo(f"2. Test your scraper: python {scraper_file}")
    click.echo(f"3. Use with CLI: jobminer scrape {scraper_name} 'python developer'")


if __name__ == '__main__':
    cli()
