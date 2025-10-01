# Infosys Detailed Job Scraper

**infosys.py** - Advanced Python web scrapers that extract comprehensive job information from individual Infosys job detail pages.

## Overview

These scrapers go beyond basic job listings to extract detailed information from each job's individual page, including:
- Complete job descriptions
- Detailed location information
- Skills and requirements
- Company details
- Similar job recommendations
- Apply URLs

## Files

### 1. `infosys.py`
- **Purpose**: Production scraper for ALL available jobs
- **Default**: Scrapes ALL jobs (1000+ jobs)
- **Use Case**: Complete data extraction, production runs

## Features

### Comprehensive Data Extraction
- **Basic Info**: Title, location, job ID from listing pages
- **Detailed Info**: Complete job descriptions, requirements, skills
- **Location Details**: Work location, state/region, country
- **Company Info**: Domain, interest group, company name
- **Application**: Direct apply URLs
- **Related Jobs**: Similar job recommendations

### Smart Processing
- **Incremental Saving**: Jobs saved after each page (no data loss)
- **Error Handling**: Continues processing even if individual jobs fail
- **Progress Tracking**: Real-time progress updates and time estimates
- **Rate Limiting**: Respectful delays between requests

### Output Format
Generates CSV files with 15 detailed columns:
- `title`, `basic_location`, `job_id`, `job_url`, `apply_url`
- `work_location`, `state_region_province`, `country`, `domain`
- `interest_group`, `skills`, `company`, `requisition_id`
- `job_description`, `similar_jobs`

## Installation

```bash
pip install requests beautifulsoup4
```

## Usage

### Complete Extraction (ALL jobs)
```bash
python scrapers/infosys/infosys.py
```
Output: `infosys_all_detailed_jobs_YYYYMMDD_HHMMSS.csv`

### Custom Configuration

Edit the scraper files to customize:

```python
# In infosys.py - change max_jobs parameter
total_scraped, total_available = scrape_detailed_jobs(
    max_jobs=100,  # Set to None for all jobs
    filepath="custom_filename.csv"
)
```
