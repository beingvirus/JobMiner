# Reliance Job Scraper 🏢💼  

A Python-based web scraper that extracts job listings and detailed descriptions from the [Reliance Industries Careers Portal](https://careers.ril.com/rilcareers/frmJobSearch.aspx) using **Selenium** and saves them into a structured CSV file.  

## ✨ Features  
- Scrapes all available job listings from the RIL Careers portal.  
- Extracts detailed information including:  
  - Job Title  
  - Posted Date  
  - Functional/Business Area  
  - Location  
  - Responsibilities  
  - Education Requirement  
  - Experience Requirement  
  - Skills & Competencies  
- Handles pagination automatically.  
- Exports data to a CSV file (`ril_all_jobs_details.csv`).  

## 🛠️ Installation  

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/ril-job-scraper.git
   cd ril-job-scraper
   ```
   
2. **Set up a virtual environment (recommended)**
   ```bash
    python -m venv venv
    source venv/bin/activate   # On Linux/Mac
    venv\Scripts\activate      # On Windows
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
