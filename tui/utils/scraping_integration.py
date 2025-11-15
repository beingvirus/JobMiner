"""
Integration utilities for connecting TUI with existing JobMiner scrapers.

This module provides the bridge between the TUI interface and the 
existing scraper implementations, handling asynchronous operations
and real-time progress updates.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from jobminer_cli import discover_scrapers, load_scraper_class
from base_scraper import JobListing
from database import get_db_manager, save_jobs_to_db


class ScrapingTask:
    """Represents a scraping task with progress tracking."""
    
    def __init__(self, scraper_name: str, search_term: str, location: str = "", pages: int = 2):
        self.scraper_name = scraper_name
        self.search_term = search_term
        self.location = location
        self.pages = pages
        self.status = "pending"
        self.progress = 0
        self.jobs_found = 0
        self.error_message = ""
        self.results: List[JobListing] = []
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        
    def to_dict(self) -> Dict:
        """Convert task to dictionary for serialization."""
        return {
            "scraper_name": self.scraper_name,
            "search_term": self.search_term,
            "location": self.location,
            "pages": self.pages,
            "status": self.status,
            "progress": self.progress,
            "jobs_found": self.jobs_found,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class ScrapingManager:
    """Manages scraping tasks and provides real-time updates."""
    
    def __init__(self):
        self.active_tasks: Dict[str, ScrapingTask] = {}
        self.scrapers = discover_scrapers()
        self.logger = logging.getLogger(__name__)
        
    def create_task(self, scraper_name: str, search_term: str, location: str = "", pages: int = 2) -> str:
        """Create a new scraping task."""
        task_id = f"{scraper_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task = ScrapingTask(scraper_name, search_term, location, pages)
        self.active_tasks[task_id] = task
        return task_id
    
    def get_task(self, task_id: str) -> Optional[ScrapingTask]:
        """Get a task by ID."""
        return self.active_tasks.get(task_id)
    
    def get_active_tasks(self) -> List[ScrapingTask]:
        """Get all active tasks."""
        return [task for task in self.active_tasks.values() if task.status in ["pending", "running", "paused"]]
    
    async def run_task(self, task_id: str, progress_callback: Optional[Callable] = None) -> bool:
        """
        Run a scraping task asynchronously with progress updates.
        
        Args:
            task_id: ID of the task to run
            progress_callback: Optional callback function for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return False
        
        if task.scraper_name not in self.scrapers:
            task.status = "error"
            task.error_message = f"Scraper '{task.scraper_name}' not found"
            return False
        
        try:
            # Update task status
            task.status = "running"
            task.started_at = datetime.now()
            task.progress = 0
            
            if progress_callback:
                await progress_callback(task_id, "Initializing scraper...", 0)
            
            # Load the scraper class
            scraper_path = self.scrapers[task.scraper_name]
            scraper_class = load_scraper_class(scraper_path)
            
            if not scraper_class:
                task.status = "error"
                task.error_message = "Failed to load scraper class"
                return False
            
            # Initialize scraper
            scraper = scraper_class()
            
            if progress_callback:
                await progress_callback(task_id, "Starting job search...", 10)
            
            # Start scraping
            jobs = []
            
            # Simulate progress for demo (in real implementation, this would be integrated with actual scraper)
            for i in range(task.pages):
                if task.status == "cancelled":
                    break
                
                page_progress = int(20 + (i / task.pages) * 60)
                task.progress = page_progress
                
                if progress_callback:
                    await progress_callback(task_id, f"Scraping page {i + 1}/{task.pages}...", page_progress)
                
                # Simulate page scraping delay
                await asyncio.sleep(1)
                
                # For demo purposes, generate some sample jobs
                page_jobs = self._generate_sample_jobs(task.search_term, task.location, 10)
                jobs.extend(page_jobs)
                task.jobs_found = len(jobs)
                
                if progress_callback:
                    await progress_callback(task_id, f"Found {len(jobs)} jobs so far...", page_progress)
            
            if task.status != "cancelled":
                # Save results
                task.progress = 85
                if progress_callback:
                    await progress_callback(task_id, "Saving results...", 85)
                
                await asyncio.sleep(0.5)
                
                # Save to database if enabled
                if get_db_manager():
                    saved_count = save_jobs_to_db(jobs, task.scraper_name)
                    self.logger.info(f"Saved {saved_count} jobs to database")
                
                # Save to JSON file
                output_file = f"jobs_{task_id}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump([job.__dict__ for job in jobs], f, indent=2, default=str)
                
                task.results = jobs
                task.status = "completed"
                task.completed_at = datetime.now()
                task.progress = 100
                
                if progress_callback:
                    await progress_callback(task_id, f"Completed! Found {len(jobs)} jobs", 100)
            
            return True
            
        except Exception as e:
            task.status = "error"
            task.error_message = str(e)
            task.completed_at = datetime.now()
            self.logger.error(f"Error in scraping task {task_id}: {e}")
            
            if progress_callback:
                await progress_callback(task_id, f"Error: {str(e)}", task.progress)
            
            return False
    
    def pause_task(self, task_id: str) -> bool:
        """Pause a running task."""
        task = self.get_task(task_id)
        if task and task.status == "running":
            task.status = "paused"
            return True
        return False
    
    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task."""
        task = self.get_task(task_id)
        if task and task.status == "paused":
            task.status = "running"
            return True
        return False
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        task = self.get_task(task_id)
        if task and task.status in ["pending", "running", "paused"]:
            task.status = "cancelled"
            task.completed_at = datetime.now()
            return True
        return False
    
    def _generate_sample_jobs(self, search_term: str, location: str, count: int) -> List[JobListing]:
        """Generate sample job listings for demonstration."""
        companies = ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Spotify", "Uber", "Airbnb", "Tesla"]
        job_types = ["Full-time", "Part-time", "Contract", "Remote"]
        experience_levels = ["Entry-level", "Mid-level", "Senior", "Lead", "Principal"]
        
        jobs = []
        for i in range(count):
            company = companies[i % len(companies)]
            job_type = job_types[i % len(job_types)]
            exp_level = experience_levels[i % len(experience_levels)]
            
            job = JobListing(
                title=f"{exp_level} {search_term} {i + 1}",
                company=company,
                location=location or "Remote",
                description=f"Exciting opportunity for a {search_term} at {company}. We are looking for talented individuals to join our team.",
                salary=f"${80 + (i * 10)}k - ${120 + (i * 15)}k",
                job_type=job_type,
                experience_level=exp_level,
                posted_date=f"{i + 1} days ago",
                job_url=f"https://example.com/jobs/{company.lower()}-{i}",
                scraped_at=datetime.now()
            )
            jobs.append(job)
        
        return jobs
    
    def get_task_summary(self) -> Dict:
        """Get summary of all tasks."""
        all_tasks = list(self.active_tasks.values())
        
        return {
            "total_tasks": len(all_tasks),
            "running": len([t for t in all_tasks if t.status == "running"]),
            "completed": len([t for t in all_tasks if t.status == "completed"]),
            "failed": len([t for t in all_tasks if t.status == "error"]),
            "paused": len([t for t in all_tasks if t.status == "paused"]),
            "total_jobs_found": sum(t.jobs_found for t in all_tasks),
        }


# Global scraping manager instance
_scraping_manager = None


def get_scraping_manager() -> ScrapingManager:
    """Get the global scraping manager instance."""
    global _scraping_manager
    if _scraping_manager is None:
        _scraping_manager = ScrapingManager()
    return _scraping_manager