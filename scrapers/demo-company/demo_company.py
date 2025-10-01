from bs4 import BeautifulSoup
import json

def scrape_demo():
    """
    Demo scraper that extracts job data from a local HTML file.
    """
    with open("demo_jobs.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for job_div in soup.find_all("div", class_="job"):
        job = {
            "title": job_div.find("h2", class_="title").get_text(strip=True),
            "company": job_div.find("span", class_="company").get_text(strip=True),
            "location": job_div.find("span", class_="location").get_text(strip=True),
            "link": job_div.find("a", class_="link")["href"]
        }
        jobs.append(job)

    return jobs

if __name__ == "__main__":
    scraped_jobs = scrape_demo()
    print(json.dumps(scraped_jobs, indent=2, ensure_ascii=False))