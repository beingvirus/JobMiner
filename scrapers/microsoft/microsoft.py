import requests
import logging
import time
import json
import csv
from typing import List

class MicrosoftScraperAPI:
    def __init__(self):
        self.base_api = "https://gcsservices.careers.microsoft.com/search/api/v1/search"
        self.logger = logging.getLogger("MicrosoftScraperAPI")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(handler)

    def _get_current_date(self):
        return time.strftime("%Y-%m-%d")

    def scrape_jobs(self, max_pages=2) -> List[dict]:
        jobs = []
        for page in range(1, max_pages+1):
            params = {
                "l": "en_us",
                "pg": page,
                "pgSz": 20,
                "o": "Relevance",
                "flt": "true"
            }
            self.logger.info(f"Fetching jobs page {page}")
            resp = requests.get(self.base_api, params=params)
            data = resp.json()

            if "operationResult" not in data or "result" not in data["operationResult"]:
                self.logger.warning(f"No jobs found in response for page {page}")
                continue

            for item in data["operationResult"]["result"]["jobs"]:
                job = {
                    "title": item.get("title"),
                    "posted_date": item.get("properties", {}).get("postedDate", self._get_current_date()),
                    "job_url": f"https://jobs.careers.microsoft.com/global/en/job/{item.get('jobId')}/{item.get('title').replace(' ', '-')}",
                    "company": "Microsoft"
                }
                jobs.append(job)

        self.logger.info(f"Collected {len(jobs)} jobs total")
        return jobs

    def save_to_json(self, jobs: List[dict], filename="microsoft_jobs.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=4)
        self.logger.info(f"Saved {len(jobs)} jobs to {filename}")

    def save_to_csv(self, jobs: List[dict], filename="microsoft_jobs.csv"):
        if not jobs:
            self.logger.warning("No jobs to save to CSV")
            return

        keys = jobs[0].keys()
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(jobs)
        self.logger.info(f"Saved {len(jobs)} jobs to {filename}")


def main():
    scraper = MicrosoftScraperAPI()
    jobs = scraper.scrape_jobs(max_pages=2)
    
    for job in jobs[:5]:  # Print first 5 jobs
        print(job)
    
    scraper.save_to_json(jobs, "microsoft_jobs.json")
    scraper.save_to_csv(jobs, "microsoft_jobs.csv")


if __name__ == "__main__":
    main()
