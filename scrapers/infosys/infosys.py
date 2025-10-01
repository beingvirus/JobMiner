import requests
from bs4 import BeautifulSoup
import time
import csv
import re
from urllib.parse import urljoin, urlparse, parse_qs
import json
import os
from datetime import datetime

BASE_URL = "https://digitalcareers.infosys.com/infosys/global-careers?location=&keyword="

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; job-scraper/1.0; +https://infosys.com/)",
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text

def parse_job_details(html, job_url):
    """Parse detailed job information from job detail page"""
    soup = BeautifulSoup(html, "html.parser")
    
    job_details = {
        "job_url": job_url,
        "apply_url": "",
        "work_location": "",
        "state_region_province": "",
        "country": "",
        "domain": "",
        "interest_group": "",
        "skills": "",
        "company": "",
        "requisition_id": "",
        "job_description": "",
        "similar_jobs": []
    }
    
    # Extract apply URL
    apply_link = soup.select_one('a.infosys-apply-link.primary-call-to-action')
    if apply_link:
        job_details["apply_url"] = apply_link.get("href", "")
    
    # Extract job details from left section
    left_section = soup.select_one('.description-page-left')
    if left_section:
        # Work Location
        work_location = left_section.select_one('#custom_field_work-location')
        if work_location:
            job_details["work_location"] = work_location.get_text(strip=True)
        
        # State/Region/Province
        state_region = left_section.select_one('#custom_field_state-region-province')
        if state_region:
            job_details["state_region_province"] = state_region.get_text(strip=True)
        
        # Country
        country = left_section.select_one('#custom_field_country')
        if country:
            job_details["country"] = country.get_text(strip=True)
        
        # Domain
        domain = left_section.select_one('#custom_field_domain')
        if domain:
            job_details["domain"] = domain.get_text(strip=True)
        
        # Interest Group
        interest_group = left_section.select_one('#custom_field_interest-group')
        if interest_group:
            job_details["interest_group"] = interest_group.get_text(strip=True)
        
        # Skills
        skills = left_section.select_one('#custom_field_skillset')
        if skills:
            job_details["skills"] = skills.get_text(strip=True)
        
        # Company
        company = left_section.select_one('#custom_field_company')
        if company:
            job_details["company"] = company.get_text(strip=True)
        
        # Requisition ID
        req_id = left_section.select_one('#custom_field_reqid')
        if req_id:
            job_details["requisition_id"] = req_id.get_text(strip=True)
    
    # Extract job description from right section
    right_section = soup.select_one('.description-page-right')
    if right_section:
        # Get all text content and clean it up
        description_text = right_section.get_text(separator='\n', strip=True)
        # Remove the "Job description" title
        if description_text.startswith("Job description"):
            description_text = description_text[len("Job description"):].strip()
        job_details["job_description"] = description_text
    
    # Extract similar jobs
    similar_jobs_section = soup.select('#similar_jobs_list .ais-Hits-item')
    similar_jobs = []
    for similar_job in similar_jobs_section:
        job_link = similar_job.select_one('a.job')
        if job_link:
            title_elem = similar_job.select_one('.similar-job-title')
            location_elem = similar_job.select_one('.similar-job-location')
            
            similar_job_data = {
                "title": title_elem.get_text(strip=True) if title_elem else "",
                "location": location_elem.get_text(strip=True) if location_elem else "",
                "url": job_link.get("href", "")
            }
            similar_jobs.append(similar_job_data)
    
    job_details["similar_jobs"] = json.dumps(similar_jobs)  # Store as JSON string for CSV
    
    return job_details

def parse_jobs_list(html, base_url):
    """Parse job listings from main page"""
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    
    # Find all job links with class "job"
    for job_link in soup.select("a.job"):
        # Extract job title
        title_elem = job_link.select_one(".job-title")
        title = title_elem.get_text(strip=True) if title_elem else "N/A"
        
        # Extract location - combine all location inline divs
        location_parts = []
        for loc_elem in job_link.select(".job-location .location-inline"):
            text = loc_elem.get_text(strip=True)
            if text and text not in [",", "-"]:
                location_parts.append(text)
        location = " ".join(location_parts) if location_parts else "N/A"
        
        # Extract job ID
        job_id_elem = job_link.select_one(".js-job-reqid .location-inline")
        job_id = job_id_elem.get_text(strip=True) if job_id_elem else "N/A"
        
        # Get the job detail link
        link = job_link.get("href")
        if link:
            link = urljoin(base_url, link)
        
        jobs.append({
            "title": title,
            "location": location,
            "job_id": job_id,
            "link": link,
        })
    
    return jobs

def get_next_page_url(html, current_url):
    """Extract the next page URL from pagination"""
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one('a.pagination-button.right[rel="next"]')
    if next_link and next_link.get("href"):
        return urljoin(current_url, next_link.get("href"))
    return None

def get_total_jobs_count(html):
    """Extract total number of jobs from the summary text"""
    soup = BeautifulSoup(html, "html.parser")
    summary = soup.select_one(".sumarry p")
    if summary:
        text = summary.get_text()
        # Extract number from text like "Showing 1 to 25 of 210 matching jobs"
        match = re.search(r'of (\d+) matching jobs', text)
        if match:
            return int(match.group(1))
    return None

def scrape_all_detailed_jobs():
    """Scrape detailed information for ALL available jobs"""
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"infosys_all_detailed_jobs_{timestamp}.csv"
    
    # CSV headers for detailed job information
    fieldnames = [
        "title", "basic_location", "job_id", "job_url", "apply_url",
        "work_location", "state_region_province", "country", "domain",
        "interest_group", "skills", "company", "requisition_id",
        "job_description", "similar_jobs"
    ]
    
    # Initialize CSV file
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
    
    current_url = BASE_URL
    page_count = 0
    total_jobs_scraped = 0
    failed_jobs = 0
    
    # Get total job count
    try:
        html = fetch_page(BASE_URL)
        total_jobs = get_total_jobs_count(html)
        if total_jobs:
            print(f"🎯 Total jobs available: {total_jobs}")
        else:
            print("❓ Could not determine total job count")
    except Exception as e:
        print(f"❌ Could not fetch initial page: {e}")
        total_jobs = None
    
    print("=" * 100)
    print("🚀 INFOSYS COMPLETE DETAILED JOB SCRAPER")
    print("=" * 100)
    print("📋 Scraping detailed information for ALL available jobs...")
    print("⏱️  This will take several hours as we fetch each job's detail page")
    print("💾 Jobs will be saved incrementally after each page")
    print(f"📁 Output file: {filepath}")
    print("=" * 100)
    
    start_time = time.time()
    
    while current_url:
        page_count += 1
        page_start_time = time.time()
        
        print(f"\n📄 Processing page {page_count}")
        print(f"🔗 URL: {current_url}")
        
        try:
            # Get job list from current page
            html = fetch_page(current_url)
            jobs_list = parse_jobs_list(html, BASE_URL)
            
            if not jobs_list:
                print(f"❌ No jobs found on page {page_count}. Stopping.")
                break
            
            print(f"📊 Found {len(jobs_list)} jobs on page {page_count}")
            
            # Process each job for detailed information
            page_detailed_jobs = []
            page_failed = 0
            
            for i, job in enumerate(jobs_list, 1):
                job_start_time = time.time()
                print(f"  🔍 [{i:2d}/{len(jobs_list)}] {job['title'][:60]}...", end="")
                
                try:
                    # Fetch detailed job page
                    job_html = fetch_page(job['link'])
                    detailed_job = parse_job_details(job_html, job['link'])
                    
                    # Combine basic info with detailed info
                    combined_job = {
                        "title": job['title'],
                        "basic_location": job['location'],
                        "job_id": job['job_id'],
                        **detailed_job
                    }
                    
                    page_detailed_jobs.append(combined_job)
                    total_jobs_scraped += 1
                    
                    job_time = time.time() - job_start_time
                    print(f" ✅ ({job_time:.1f}s)")
                    
                    # Small delay between job detail requests
                    time.sleep(1.5)
                    
                except Exception as e:
                    print(f" ❌ Error: {str(e)[:30]}...")
                    failed_jobs += 1
                    page_failed += 1
                    
                    # Add basic job info even if detailed scraping fails
                    basic_job = {
                        "title": job['title'],
                        "basic_location": job['location'],
                        "job_id": job['job_id'],
                        "job_url": job['link'],
                        "apply_url": "",
                        "work_location": "",
                        "state_region_province": "",
                        "country": "",
                        "domain": "",
                        "interest_group": "",
                        "skills": "",
                        "company": "",
                        "requisition_id": "",
                        "job_description": "ERROR: Could not fetch detailed information",
                        "similar_jobs": ""
                    }
                    page_detailed_jobs.append(basic_job)
                    total_jobs_scraped += 1
            
            # Save jobs from this page to CSV
            if page_detailed_jobs:
                with open(filepath, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerows(page_detailed_jobs)
                
                page_time = time.time() - page_start_time
                success_rate = ((len(page_detailed_jobs) - page_failed) / len(page_detailed_jobs)) * 100
                
                print(f"\n  ✅ Page {page_count} completed in {page_time:.1f}s")
                print(f"  💾 Saved {len(page_detailed_jobs)} jobs ({success_rate:.1f}% success rate)")
                print(f"  📊 Total progress: {total_jobs_scraped}/{total_jobs or '?'} jobs")
                
                if total_jobs:
                    progress = (total_jobs_scraped / total_jobs) * 100
                    print(f"  📈 Overall progress: {progress:.1f}%")
                    
                    # Estimate remaining time
                    elapsed = time.time() - start_time
                    if total_jobs_scraped > 0:
                        avg_time_per_job = elapsed / total_jobs_scraped
                        remaining_jobs = total_jobs - total_jobs_scraped
                        estimated_remaining = (remaining_jobs * avg_time_per_job) / 3600  # in hours
                        print(f"  ⏱️  Estimated time remaining: {estimated_remaining:.1f} hours")
            
            # Get next page URL
            next_url = get_next_page_url(html, current_url)
            if not next_url:
                print(f"\n🏁 Reached the last page (page {page_count})")
                break
            
            current_url = next_url
            
            # Longer delay between pages
            print(f"  ⏳ Waiting 5 seconds before next page...")
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Error processing page {page_count}: {e}")
            print("⏭️  Continuing to next page...")
            continue
    
    return total_jobs_scraped, total_jobs, failed_jobs, filepath

if __name__ == "__main__":
    print("🎯 Starting COMPLETE Infosys detailed job scraping...")
    print("⚠️  This will scrape ALL available jobs and may take several hours!")
    print("💡 Press Ctrl+C to stop at any time (progress will be saved)")
    
    try:
        total_scraped, total_available, failed, output_file = scrape_all_detailed_jobs()
        
        end_time = time.time()
        
        print("\n" + "=" * 100)
        print("🎉 COMPLETE DETAILED SCRAPING FINISHED!")
        print("=" * 100)
        print(f"✅ Total jobs scraped: {total_scraped}")
        print(f"❌ Failed jobs: {failed}")
        print(f"📊 Success rate: {((total_scraped - failed) / total_scraped * 100):.1f}%")
        
        if total_available:
            print(f"🎯 Total jobs available: {total_available}")
            print(f"📈 Coverage: {total_scraped/total_available*100:.1f}%")
        
        print(f"💾 Complete data saved to: {output_file}")
        print(f"📁 File size: {os.path.getsize(output_file) / (1024*1024):.1f} MB")
        print("=" * 100)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Scraping interrupted by user")
        print("💾 All progress has been saved to the CSV file")
        print("🔄 You can resume by running the script again")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💾 Check the CSV file for any data that was saved")
