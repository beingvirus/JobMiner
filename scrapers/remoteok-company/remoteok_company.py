from selenium import webdriver
from bs4 import BeautifulSoup

URL = "https://remoteok.io/remote-dev+python-jobs"

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

driver.get(URL)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

jobs = []
for job in soup.find_all("tr", class_="job"):
    title_tag = job.find("h2")
    company_tag = job.find("h3")
    link = job.get("data-href")
    if title_tag and company_tag and link:
        jobs.append({
            "title": title_tag.text.strip(),
            "company": company_tag.text.strip(),
            "link": "https://remoteok.io" + link
        })

driver.quit()

print("\nFetched Jobs:\n" + "-"*50)
for i, job in enumerate(jobs, 1):
    print(f"{i}. {job['title']} at {job['company']}")
    print(f"   Link: {job['link']}\n")
