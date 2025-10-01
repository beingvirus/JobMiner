from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

BASE_URL = "https://careers.ril.com/rilcareers/frmJobSearch.aspx"

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def scrape_jobs(driver):
    driver.get(BASE_URL)
    jobs = []

    while True:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "MainContent_rgJobs"))
        )

        rows = driver.find_elements(By.CSS_SELECTOR, "#MainContent_rgJobs tbody tr")
        for row in rows[:-1]:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) < 5:
                continue
            job = {
                "Title": cols[1].text.strip(),
                "Link": cols[1].find_element(By.TAG_NAME, "a").get_attribute("href"),
                "Functional Area": cols[2].text.strip(),
                "Location": cols[3].text.strip(),
                "Posted On": cols[4].text.strip(),
            }
            jobs.append(job)

        try:
            next_btn = driver.find_element(By.ID, "MainContent_rgJobs_lnkNext")
            if "aspNetDisabled" in next_btn.get_attribute("class"):
                break
            next_btn.click()
            time.sleep(2)
        except:
            break

    return jobs

def scrape_job_details(driver, job_url):
    driver.get(job_url)
    job_data = {}

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "contentarea"))
        )

        job_data["Title"] = driver.find_element(By.ID, "MainContent_lblJobTitle").text.strip()
        job_data["Posted Date"] = driver.find_element(By.ID, "MainContent_lblPostedDate").text.strip()
        job_data["Function/Business Area"] = driver.find_element(By.ID, "MainContent_lblSec").text.strip()
        job_data["Location"] = driver.find_element(By.ID, "MainContent_lblLoc").text.strip()
        job_data["Responsibilities"] = driver.find_element(By.ID, "MainContent_lblSummRole").text.strip()
        job_data["Education Requirement"] = driver.find_element(By.ID, "MainContent_lblEduReq").text.strip()
        job_data["Experience Requirement"] = driver.find_element(By.ID, "MainContent_lblExpReq").text.strip()

        # Skills table
        skills_table = driver.find_elements(By.CSS_SELECTOR, "table.MsoTableGrid tbody tr")[1:]
        skills_list = []
        for row in skills_table:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                skill_name = cols[0].text.strip()
                skill_rating = cols[1].text.strip()
                skills_list.append(f"{skill_name} ({skill_rating})")
        job_data["Skills & Competencies"] = ", ".join(skills_list)

    except Exception as e:
        print(f"Failed to scrape {job_url}: {e}")

    return job_data

if __name__ == "__main__":
    driver = init_driver()

    print("🚀 Scraping job listings...")
    jobs_list = scrape_jobs(driver)
    print(f"✅ Found {len(jobs_list)} jobs.")

    all_jobs_details = []
    for job in jobs_list:
        print(f"🔍 Scraping details for: {job['Title']}")
        details = scrape_job_details(driver, job["Link"])
        all_jobs_details.append(details)
        time.sleep(1)

    driver.quit()

    df = pd.DataFrame(all_jobs_details)
    df.to_csv("ril_all_jobs_details.csv", index=False, encoding="utf-8-sig")
    print(f"🎉 Scraping completed, saved {len(all_jobs_details)} jobs to ril_all_jobs_details.csv")
