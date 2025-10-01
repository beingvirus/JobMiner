# JobMiner Examples

This directory contains example scripts demonstrating various JobMiner features and usage patterns.

## Available Examples

### 1. Basic Usage (`basic_usage.py`)
Demonstrates the fundamental JobMiner workflow:
- Initialize a scraper
- Scrape jobs with search parameters
- Save results to JSON and CSV formats
- Display sample job listings

```bash
cd examples
python3 basic_usage.py
```

### 2. Database Usage (`database_usage.py`)
Shows how to use JobMiner with database integration:
- Enable database storage
- Save scraped jobs to database
- Query and search stored jobs
- Generate database statistics
- Retrieve jobs by various filters

```bash
cd examples
python3 database_usage.py
```

### 3. Batch Scraping (`batch_scraping.py`)
Demonstrates batch processing of multiple search queries:
- Define multiple search parameters
- Process searches in sequence
- Combine and analyze results
- Generate timestamped output files

```bash
cd examples
python3 batch_scraping.py
```

## Running Examples

1. **Prerequisites**: Make sure you have installed JobMiner dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Run from examples directory**:
   ```bash
   cd examples
   python3 [example_script.py]
   ```

3. **Check outputs**: Examples will create various output files:
   - `*.json` - Job data in JSON format
   - `*.csv` - Job data in CSV format
   - `*.db` - SQLite database files (for database examples)

## Example Outputs

After running the examples, you'll find various output files:

- **basic_jobs.json/csv** - Results from basic usage example
- **jobminer_example.db** - Database from database usage example
- **batch_jobs_[timestamp].json/csv** - Results from batch scraping

## Customizing Examples

Feel free to modify these examples:

- **Change search terms**: Update the search queries in the scripts
- **Adjust locations**: Modify location parameters
- **Add more scrapers**: When you create new scrapers, update the import statements
- **Modify output formats**: Change file names or add additional export formats

## Creating Your Own Scripts

Use these examples as templates for your own JobMiner scripts:

1. **Import the necessary modules**:
   ```python
   from scrapers.your_scraper.your_scraper import YourScraper
   from database import DatabaseManager  # if using database
   ```

2. **Initialize scraper with your preferred settings**:
   ```python
   scraper = YourScraper(delay=2.0)  # Adjust delay as needed
   ```

3. **Define your search parameters and run scraping**:
   ```python
   jobs = scraper.scrape_jobs("your search term", "location", max_pages=3)
   ```

4. **Process and save results as needed**

## Tips for Real Scrapers

When adapting these examples for real job site scrapers:

- **Respect rate limits**: Increase delays between requests
- **Handle errors gracefully**: Add try-catch blocks for network issues
- **Monitor for changes**: Job sites may change their HTML structure
- **Use appropriate headers**: Some sites require specific user agents
- **Consider legal aspects**: Always check robots.txt and terms of service

## Need Help?

- Check the main [README.md](../README.md) for general JobMiner documentation
- Look at individual scraper README files in the `scrapers/` directory
- Review the [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines
