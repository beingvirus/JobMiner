# JobMiner 🔍

JobMiner is a powerful Python-based web scraping toolkit for extracting and organizing job listings from multiple websites into structured data. Built with modularity and extensibility in mind, it provides a robust foundation for job market analysis and automated job searching.

## ✨ Features

- **Modular Architecture**: Easy-to-extend scraper system with base classes
- **Multiple Output Formats**: Export to JSON, CSV, or both
- **Database Integration**: Optional SQLite/PostgreSQL storage with search capabilities
- **CLI Interface**: Command-line tool for easy scraping operations
- **Configuration Management**: Flexible configuration system with environment variables
- **Rate Limiting**: Built-in delays and respectful scraping practices
- **Error Handling**: Comprehensive logging and error recovery
- **Template Generation**: Quick scraper template creation for new job sites

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/beingvirus/JobMiner.git
cd JobMiner

# Install dependencies
pip install -r requirements.txt

# Optional: Install as package
pip install -e .
```

### Basic Usage

```bash
# List available scrapers
python jobminer_cli.py list-scrapers

# Run demo scraper
python jobminer_cli.py scrape demo-company "python developer" --location "san francisco" --pages 2

# Analyze scraped data
python jobminer_cli.py analyze jobs.json
```

### Python API

```python
from scrapers.demo_company.demo_company import DemoCompanyScraper

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

## 📁 Project Structure

```
JobMiner/
├── base_scraper.py              # Base scraper class with common functionality
├── jobminer_cli.py              # Command-line interface
├── config.py                    # Configuration management
├── database.py                  # Database integration (optional)
├── requirements.txt             # Project dependencies
├── setup.py                     # Package setup
├── .env.example                 # Environment variables template
├── scrapers/                    # Individual scraper implementations
│   └── demo-company/
│       ├── demo_company.py      # Demo scraper implementation
│       ├── demo_company_readme.md
│       └── requirements.txt
└── output/                      # Default output directory
```

## 🛠 Creating New Scrapers

### Using the Template Generator

```bash
# Generate a new scraper template
python jobminer_cli.py init

# Follow the prompts to create your scraper
```

### Manual Creation

1. Create a new directory in `scrapers/`
2. Implement the `BaseScraper` class:

```python
from base_scraper import BaseScraper, JobListing

class YourScraper(BaseScraper):
    def get_job_urls(self, search_term, location="", max_pages=1):
        # Implement job URL extraction
        pass
    
    def parse_job(self, job_url):
        # Implement job detail parsing
        return JobListing(...)
```

3. Test your scraper:

```bash
python your_scraper.py
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Database
JOBMINER_DATABASE_URL=sqlite:///jobminer.db

# Logging
JOBMINER_LOG_LEVEL=INFO

# Scraper settings
JOBMINER_DEFAULT_DELAY=2.0
```

### Configuration File

JobMiner automatically creates `jobminer_config.json` with default settings:

```json
{
  "default_output_format": "both",
  "output_directory": "output",
  "default_scraper_config": {
    "delay": 2.0,
    "timeout": 30,
    "max_retries": 3
  }
}
```

## feature/complete-jobminer-toolkit

## 💾 Database Integration

Enable database storage for persistent job data:

```python
from config import get_config
from database import get_db_manager

# Enable database in config
config = get_config()
config.database.enabled = True

# Save jobs to database
db_manager = get_db_manager()
db_manager.save_jobs(jobs, scraper_name="demo-company")

# Search jobs
results = db_manager.search_jobs("python developer")
```

## 📊 CLI Commands

```bash
# List available scrapers
jobminer list-scrapers

# Scrape jobs
jobminer scrape SCRAPER_NAME "SEARCH_TERM" [OPTIONS]

# Analyze results
jobminer analyze FILE_PATH

# Generate new scraper template
jobminer init
```

### CLI Options

- `--location, -l`: Search location
- `--pages, -p`: Number of pages to scrape
- `--output, -o`: Output filename
- `--format, -f`: Output format (json/csv/both)
- `--delay, -d`: Delay between requests

## 🤝 Contributing

We welcome contributions! This project is **Hacktoberfest-friendly** 🎃

### Ways to Contribute

- **Add new scrapers** for popular job sites
- **Improve existing scrapers** with better parsing
- **Add features** like advanced filtering or export options
- **Fix bugs** and improve error handling
- **Improve documentation** and examples

### Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📋 Supported Job Sites

Currently implemented scrapers:

- **Demo Company** - Template/example scraper for testing

### Planned Scrapers

- LinkedIn Jobs
- Indeed
- Glassdoor
- AngelList
- Stack Overflow Jobs
- Remote.co

*Want to add a scraper for your favorite job site? Check out our [contribution guide](CONTRIBUTING.md)!*

## 🔧 Requirements

- Python 3.8+
- requests
- beautifulsoup4
- pandas
- click
- sqlalchemy (optional, for database features)
- selenium (optional, for JavaScript-heavy sites)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the open-source community
- Hacktoberfest 2025 participant
- Inspired by the need for better job market analysis tools

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/beingvirus/JobMiner/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/beingvirus/JobMiner/discussions)
- 📖 **Documentation**: [Project Wiki](https://github.com/beingvirus/JobMiner/wiki)

---

**Happy Job Mining! 🎯**

*Made with ❤️ by the open-source community*
=======
---

## Contributors ✨

![Contributors Hall of Fame](https://contrib.rocks/image?repo=beingvirus/JobMiner)
