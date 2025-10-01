# Demo Company Scraper

This is a template scraper for JobMiner that demonstrates how to implement the `BaseScraper` class for a job site.

## Overview

The Demo Company Scraper serves as a reference implementation showing:
- How to extend the `BaseScraper` class
- Proper method implementation for `get_job_urls()` and `parse_job()`
- Mock data generation for testing purposes
- Error handling and logging practices

## Usage

```python
from demo_company import DemoCompanyScraper

# Initialize scraper
scraper = DemoCompanyScraper()

# Scrape jobs
jobs = scraper.scrape_jobs(
    search_term="python developer",
    location="san francisco",
    max_pages=2
)

# Save results
scraper.save_to_json(jobs, "jobs.json")
scraper.save_to_csv(jobs, "jobs.csv")
```

## Running the Demo

```bash
cd scrapers/demo-company
python demo_company.py
```

## Implementation Notes

### For Real Scrapers

When creating a real scraper based on this template:

1. **Update `get_job_urls()`**:
   - Build actual search URLs with proper parameters
   - Parse search result pages to extract job URLs
   - Handle pagination correctly
   - Implement proper stopping conditions

2. **Update `parse_job()`**:
   - Fetch actual job pages using `self.get_page()`
   - Use CSS selectors or XPath to extract job details
   - Handle missing fields gracefully
   - Clean and validate extracted data

3. **Add Site-Specific Logic**:
   - Handle authentication if required
   - Implement rate limiting specific to the site
   - Add custom headers or cookies if needed
   - Handle dynamic content (JavaScript) if necessary

### CSS Selectors Examples

Common patterns for job sites:

```python
# Job title
title = soup.find('h1', {'class': 'job-title'}).text

# Company name
company = soup.find('div', {'class': 'company-name'}).text

# Location
location = soup.find('span', {'class': 'job-location'}).text

# Description
description = soup.find('div', {'class': 'job-description'}).text

# Salary (optional)
salary_elem = soup.find('span', {'class': 'salary'})
salary = salary_elem.text if salary_elem else None
```

## Requirements

See `requirements.txt` in this directory for specific dependencies.

## Contributing

When contributing a new scraper:
1. Follow this template structure
2. Include comprehensive error handling
3. Add proper logging
4. Test with various search terms
5. Document any site-specific quirks
6. Include usage examples
