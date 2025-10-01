"""
Database integration for JobMiner.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from base_scraper import JobListing
from config import get_config

Base = declarative_base()


class JobRecord(Base):
    """Database model for job listings."""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    salary = Column(String(100))
    job_type = Column(String(50))
    experience_level = Column(String(50))
    posted_date = Column(String(50))
    job_url = Column(String(1000))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    scraper_name = Column(String(100))
    
    def to_job_listing(self) -> JobListing:
        """Convert database record to JobListing object."""
        return JobListing(
            title=self.title,
            company=self.company,
            location=self.location,
            description=self.description,
            salary=self.salary,
            job_type=self.job_type,
            experience_level=self.experience_level,
            posted_date=self.posted_date,
            job_url=self.job_url,
            scraped_at=self.scraped_at
        )
    
    @classmethod
    def from_job_listing(cls, job: JobListing, scraper_name: str = None):
        """Create database record from JobListing object."""
        return cls(
            title=job.title,
            company=job.company,
            location=job.location,
            description=job.description,
            salary=job.salary,
            job_type=job.job_type,
            experience_level=job.experience_level,
            posted_date=job.posted_date,
            job_url=job.job_url,
            scraped_at=job.scraped_at,
            scraper_name=scraper_name
        )


class DatabaseManager:
    """Manages database operations for JobMiner."""
    
    def __init__(self, database_url: str = None):
        """Initialize database manager."""
        config = get_config()
        
        if database_url is None:
            database_url = config.database.url
        
        self.engine = create_engine(
            database_url,
            echo=config.database.echo
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Create tables
        self.create_tables()
    
    def create_tables(self):
        """Create database tables."""
        Base.metadata.create_all(bind=self.engine)
        self.logger.info("Database tables created/verified")
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    def save_jobs(self, jobs: List[JobListing], scraper_name: str = None) -> int:
        """
        Save job listings to database.
        
        Args:
            jobs: List of JobListing objects
            scraper_name: Name of the scraper that collected these jobs
            
        Returns:
            Number of jobs saved
        """
        if not jobs:
            return 0
        
        session = self.get_session()
        saved_count = 0
        
        try:
            for job in jobs:
                # Check if job already exists (by URL)
                existing = session.query(JobRecord).filter_by(job_url=job.job_url).first()
                
                if not existing:
                    job_record = JobRecord.from_job_listing(job, scraper_name)
                    session.add(job_record)
                    saved_count += 1
                else:
                    self.logger.debug(f"Job already exists: {job.job_url}")
            
            session.commit()
            self.logger.info(f"Saved {saved_count} new jobs to database")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving jobs to database: {e}")
            raise
        finally:
            session.close()
        
        return saved_count
    
    def get_jobs(self, 
                 limit: int = 100,
                 company: str = None,
                 location: str = None,
                 job_type: str = None,
                 scraper_name: str = None) -> List[JobListing]:
        """
        Retrieve jobs from database with optional filters.
        
        Args:
            limit: Maximum number of jobs to return
            company: Filter by company name
            location: Filter by location
            job_type: Filter by job type
            scraper_name: Filter by scraper name
            
        Returns:
            List of JobListing objects
        """
        session = self.get_session()
        
        try:
            query = session.query(JobRecord)
            
            # Apply filters
            if company:
                query = query.filter(JobRecord.company.ilike(f'%{company}%'))
            if location:
                query = query.filter(JobRecord.location.ilike(f'%{location}%'))
            if job_type:
                query = query.filter(JobRecord.job_type.ilike(f'%{job_type}%'))
            if scraper_name:
                query = query.filter(JobRecord.scraper_name == scraper_name)
            
            # Order by scraped_at descending and limit
            records = query.order_by(JobRecord.scraped_at.desc()).limit(limit).all()
            
            # Convert to JobListing objects
            jobs = [record.to_job_listing() for record in records]
            
            return jobs
            
        finally:
            session.close()
    
    def get_job_stats(self) -> dict:
        """Get statistics about jobs in database."""
        session = self.get_session()
        
        try:
            total_jobs = session.query(JobRecord).count()
            
            # Company stats
            company_stats = session.query(
                JobRecord.company,
                session.query(JobRecord).filter(
                    JobRecord.company == JobRecord.company
                ).count().label('count')
            ).group_by(JobRecord.company).order_by('count DESC').limit(10).all()
            
            # Location stats
            location_stats = session.query(
                JobRecord.location,
                session.query(JobRecord).filter(
                    JobRecord.location == JobRecord.location
                ).count().label('count')
            ).group_by(JobRecord.location).order_by('count DESC').limit(10).all()
            
            # Scraper stats
            scraper_stats = session.query(
                JobRecord.scraper_name,
                session.query(JobRecord).filter(
                    JobRecord.scraper_name == JobRecord.scraper_name
                ).count().label('count')
            ).group_by(JobRecord.scraper_name).order_by('count DESC').all()
            
            return {
                'total_jobs': total_jobs,
                'top_companies': [(comp, count) for comp, count in company_stats],
                'top_locations': [(loc, count) for loc, count in location_stats],
                'scraper_stats': [(scraper, count) for scraper, count in scraper_stats]
            }
            
        finally:
            session.close()
    
    def search_jobs(self, search_term: str, limit: int = 100) -> List[JobListing]:
        """
        Search jobs by title or description.
        
        Args:
            search_term: Term to search for
            limit: Maximum number of results
            
        Returns:
            List of matching JobListing objects
        """
        session = self.get_session()
        
        try:
            query = session.query(JobRecord).filter(
                (JobRecord.title.ilike(f'%{search_term}%')) |
                (JobRecord.description.ilike(f'%{search_term}%'))
            ).order_by(JobRecord.scraped_at.desc()).limit(limit)
            
            records = query.all()
            jobs = [record.to_job_listing() for record in records]
            
            return jobs
            
        finally:
            session.close()
    
    def delete_old_jobs(self, days: int = 30) -> int:
        """
        Delete jobs older than specified days.
        
        Args:
            days: Number of days to keep jobs
            
        Returns:
            Number of jobs deleted
        """
        session = self.get_session()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            deleted_count = session.query(JobRecord).filter(
                JobRecord.scraped_at < cutoff_date
            ).delete()
            
            session.commit()
            self.logger.info(f"Deleted {deleted_count} old jobs")
            
            return deleted_count
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error deleting old jobs: {e}")
            raise
        finally:
            session.close()
    
    def close(self):
        """Close database connection."""
        self.engine.dispose()


# Global database manager instance
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance."""
    global _db_manager
    
    config = get_config()
    
    if not config.database.enabled:
        return None
    
    if _db_manager is None:
        _db_manager = DatabaseManager()
    
    return _db_manager


def save_jobs_to_db(jobs: List[JobListing], scraper_name: str = None) -> int:
    """Convenience function to save jobs to database."""
    db_manager = get_db_manager()
    if db_manager:
        return db_manager.save_jobs(jobs, scraper_name)
    return 0
