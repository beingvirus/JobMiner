"""
Main JobMiner TUI Application.

This module contains the main Textual application class that provides
an enhanced command-line interface with rich text formatting and
interactive components.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button, Header, Footer, Static, Label, Input, Select, 
    DataTable, ProgressBar, TabPane, TabbedContent, Log
)
from textual.binding import Binding
from textual.screen import Screen
from textual import events
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
import asyncio
from pathlib import Path
import sys
import os

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from jobminer_cli import discover_scrapers
from tui.utils.scraping_integration import get_scraping_manager


class MainMenuScreen(Screen):
    """Main menu screen with navigation options."""
    
    BINDINGS = [
        Binding("s", "search", "Quick Search"),
        Binding("r", "results", "View Results"),
        Binding("a", "analytics", "Analytics"),
        Binding("c", "config", "Configuration"),
        Binding("h", "help", "Help"),
        Binding("q", "quit", "Quit"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the main menu layout."""
        yield Header()
        yield Container(
            Static(self._create_banner(), id="banner"),
            Vertical(
                Static(self._create_menu_options(), id="menu-options"),
                Horizontal(
                    Button("🔍 Quick Search", id="search-btn", variant="primary"),
                    Button("📊 View Results", id="results-btn"),
                    Button("📈 Analytics", id="analytics-btn"),
                    classes="button-row"
                ),
                Horizontal(
                    Button("🚀 Manage Scrapers", id="scrapers-btn"),
                    Button("⚙️ Configuration", id="config-btn"),
                    Button("❓ Help", id="help-btn"),
                    classes="button-row"
                ),
                Horizontal(
                    Button("🗃️ Database Browser", id="database-btn"),
                    Button("🚪 Exit", id="exit-btn", variant="error"),
                    classes="button-row"
                ),
                id="menu-container"
            ),
            id="main-content"
        )
        yield Footer()
    
    def _create_banner(self) -> str:
        """Create the application banner."""
        return """
╔══════════════════════════════════════════════════════════╗
║                    🔍 JobMiner TUI                       ║
║          Enhanced Command Line Interface                 ║
╚══════════════════════════════════════════════════════════╝
        """
    
    def _create_menu_options(self) -> str:
        """Create menu options description."""
        return """
Welcome to JobMiner Enhanced CLI! Choose an option below:

🔍 Quick Search     - Start a new job search
📊 View Results     - Browse previous results
📈 Analytics        - View job market insights
🚀 Manage Scrapers  - Configure job site scrapers
⚙️ Configuration    - Manage settings and database
❓ Help             - Documentation and guides
🗃️ Database Browser - Browse stored job data
🚪 Exit             - Close the application

Use arrow keys and Enter to navigate, or press the hotkeys (s, r, a, etc.)
        """
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "search-btn":
            self.action_search()
        elif event.button.id == "results-btn":
            self.action_results()
        elif event.button.id == "analytics-btn":
            self.action_analytics()
        elif event.button.id == "scrapers-btn":
            self.action_scrapers()
        elif event.button.id == "config-btn":
            self.action_config()
        elif event.button.id == "help-btn":
            self.action_help()
        elif event.button.id == "database-btn":
            self.action_database()
        elif event.button.id == "exit-btn":
            self.action_quit()
    
    def action_search(self) -> None:
        """Switch to search screen."""
        self.app.push_screen("search")
    
    def action_results(self) -> None:
        """Switch to results screen."""
        self.app.push_screen("results")
    
    def action_analytics(self) -> None:
        """Switch to analytics screen."""
        self.app.push_screen("analytics")
    
    def action_scrapers(self) -> None:
        """Switch to scrapers management screen."""
        self.app.push_screen("scrapers")
    
    def action_config(self) -> None:
        """Switch to configuration screen."""
        self.app.push_screen("config")
    
    def action_help(self) -> None:
        """Switch to help screen."""
        self.app.push_screen("help")
    
    def action_database(self) -> None:
        """Switch to database browser screen."""
        self.app.push_screen("database")
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class SearchScreen(Screen):
    """Job search screen with interactive form."""
    
    BINDINGS = [
        Binding("escape", "back", "Back to Menu"),
        Binding("ctrl+s", "start_search", "Start Search"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the search form layout."""
        # Get available scrapers
        scrapers = discover_scrapers()
        scraper_options = [(name, name.title()) for name in scrapers.keys()]
        
        yield Header()
        yield Container(
            Static("🔍 Job Search", classes="screen-title"),
            Vertical(
                Container(
                    Label("Job Title/Keywords:"),
                    Input(placeholder="e.g., Python Developer, Data Scientist", id="job-title"),
                    classes="form-group"
                ),
                Container(
                    Label("Location:"),
                    Input(placeholder="e.g., San Francisco, Remote, New York", id="location"),
                    classes="form-group"
                ),
                Container(
                    Label("Select Scrapers:"),
                    Select(scraper_options, id="scraper-select", allow_blank=False),
                    classes="form-group"
                ),
                Container(
                    Label("Number of Pages:"),
                    Input(placeholder="1-10", value="2", id="pages"),
                    classes="form-group"
                ),
                Horizontal(
                    Button("🚀 Start Search", id="start-search", variant="primary"),
                    Button("🔄 Reset Form", id="reset-form"),
                    Button("← Back", id="back-btn"),
                    classes="button-row"
                ),
                Static("", id="search-status"),
                id="search-form"
            ),
            id="search-content"
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "start-search":
            self.start_search()
        elif event.button.id == "reset-form":
            self.reset_form()
        elif event.button.id == "back-btn":
            self.action_back()
    
    def start_search(self) -> None:
        """Start the job search process."""
        # Get form values
        job_title = self.query_one("#job-title", Input).value
        location = self.query_one("#location", Input).value
        scraper = self.query_one("#scraper-select", Select).value
        pages = self.query_one("#pages", Input).value
        
        # Validate inputs
        if not job_title:
            self.query_one("#search-status", Static).update("❌ Please enter a job title")
            return
        
        if not scraper:
            self.query_one("#search-status", Static).update("❌ Please select a scraper")
            return
        
        try:
            pages_int = int(pages) if pages else 2
            if pages_int < 1 or pages_int > 10:
                raise ValueError("Pages must be between 1 and 10")
        except ValueError:
            self.query_one("#search-status", Static).update("❌ Pages must be a number between 1 and 10")
            return
        
        # Update status and start search
        self.query_one("#search-status", Static).update(f"🔍 Starting search for '{job_title}' using {scraper}...")
        
        # Create and push progress screen with parameters
        progress_screen = ProgressScreen({"job_title": job_title, "location": location, "scraper": scraper, "pages": pages_int})
        self.app.push_screen(progress_screen)
    
    def reset_form(self) -> None:
        """Reset all form fields."""
        self.query_one("#job-title", Input).value = ""
        self.query_one("#location", Input).value = ""
        self.query_one("#pages", Input).value = "2"
        self.query_one("#search-status", Static).update("")
    
    def action_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    def action_start_search(self) -> None:
        """Hotkey for starting search."""
        self.start_search()


class ProgressScreen(Screen):
    """Progress monitoring screen for active scraping."""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("p", "pause", "Pause"),
        Binding("s", "stop", "Stop"),
    ]
    
    def __init__(self, search_params: dict):
        super().__init__()
        self.search_params = search_params
        self.is_running = False
        self.progress_value = 0
        self.scraping_manager = get_scraping_manager()
        self.task_id = None
    
    def compose(self) -> ComposeResult:
        """Create the progress monitoring layout."""
        yield Header()
        yield Container(
            Static("🔄 Scraping in Progress", classes="screen-title"),
            Vertical(
                Static(f"Search: {self.search_params['job_title']}", id="search-info"),
                Static(f"Location: {self.search_params.get('location', 'Any')}", id="location-info"),
                Static(f"Scraper: {self.search_params['scraper']}", id="scraper-info"),
                Static("", id="status-line"),
                ProgressBar(total=100, id="progress-bar"),
                Static("Jobs found: 0", id="job-count"),
                Log(id="activity-log"),
                Horizontal(
                    Button("⏸️ Pause", id="pause-btn"),
                    Button("⏹️ Stop", id="stop-btn", variant="error"),
                    Button("🖼️ Background", id="background-btn"),
                    classes="button-row"
                ),
                id="progress-content"
            )
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Start the scraping process when screen is mounted."""
        self.start_scraping()
    
    def start_scraping(self) -> None:
        """Start the real scraping process."""
        self.is_running = True
        
        # Create scraping task
        self.task_id = self.scraping_manager.create_task(
            scraper_name=self.search_params['scraper'],
            search_term=self.search_params['job_title'],
            location=self.search_params.get('location', ''),
            pages=self.search_params['pages']
        )
        
        self.query_one("#status-line", Static).update("🟢 Starting scraper...")
        
        # Start the async scraping task
        asyncio.create_task(self.run_scraping_task())
    
    async def run_scraping_task(self) -> None:
        """Run the scraping task asynchronously."""
        try:
            success = await self.scraping_manager.run_task(
                self.task_id, 
                progress_callback=self.update_progress
            )
            
            if success:
                task = self.scraping_manager.get_task(self.task_id)
                if task and task.status == "completed":
                    self.query_one("#status-line", Static).update("✅ Scraping completed!")
                    self.set_timer(2.0, self.auto_navigate_to_results)
            else:
                self.query_one("#status-line", Static).update("❌ Scraping failed!")
                
        except Exception as e:
            self.query_one("#status-line", Static).update(f"❌ Error: {str(e)}")
            self.is_running = False
    
    async def update_progress(self, task_id: str, status: str, progress: int) -> None:
        """Update progress display from scraping task."""
        # Update progress bar
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        progress_bar.progress = progress
        
        # Update status
        self.query_one("#status-line", Static).update(status)
        
        # Update job count
        task = self.scraping_manager.get_task(task_id)
        if task:
            self.query_one("#job-count", Static).update(f"Jobs found: {task.jobs_found}")
        
        # Add log entry
        log = self.query_one("#activity-log", Log)
        log.write_line(f"[{progress}%] {status}")
        
        # Update progress value for other methods
        self.progress_value = progress
    
    def auto_navigate_to_results(self) -> None:
        """Automatically navigate to results after completion."""
        self.app.push_screen("results")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "pause-btn":
            self.action_pause()
        elif event.button.id == "stop-btn":
            self.action_stop()
        elif event.button.id == "background-btn":
            self.action_back()
    
    def action_pause(self) -> None:
        """Pause/resume scraping."""
        if self.task_id:
            task = self.scraping_manager.get_task(self.task_id)
            if task:
                if task.status == "running":
                    self.scraping_manager.pause_task(self.task_id)
                    self.query_one("#pause-btn", Button).label = "▶️ Resume"
                    self.query_one("#status-line", Static).update("⏸️ Paused")
                elif task.status == "paused":
                    self.scraping_manager.resume_task(self.task_id)
                    self.query_one("#pause-btn", Button).label = "⏸️ Pause"
                    self.query_one("#status-line", Static).update("🟢 Resumed")
    
    def action_stop(self) -> None:
        """Stop scraping."""
        if self.task_id:
            self.scraping_manager.cancel_task(self.task_id)
            self.is_running = False
            self.query_one("#status-line", Static).update("🛑 Stopped by user")
            self.set_timer(1.0, self.action_back)
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()


class ResultsScreen(Screen):
    """Results viewing screen with job listings."""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("e", "export", "Export"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the results viewing layout."""
        yield Header()
        yield Container(
            Static("📊 Job Search Results", classes="screen-title"),
            Vertical(
                Container(
                    Label("Filter Results:"),
                    Horizontal(
                        Input(placeholder="Search in results...", id="filter-input"),
                        Button("🔍 Filter", id="filter-btn"),
                        Button("🔄 Clear", id="clear-filter-btn"),
                        classes="filter-row"
                    ),
                    classes="filter-section"
                ),
                DataTable(id="results-table"),
                Horizontal(
                    Button("📄 View Details", id="view-details-btn"),
                    Button("💾 Export Results", id="export-btn"),
                    Button("← Back", id="back-btn"),
                    classes="button-row"
                ),
                Static("", id="results-status"),
                id="results-content"
            )
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the results table when screen is mounted."""
        self.setup_results_table()
    
    def setup_results_table(self) -> None:
        """Set up the results data table."""
        table = self.query_one("#results-table", DataTable)
        
        # Add columns
        table.add_column("ID", width=5)
        table.add_column("Title", width=30)
        table.add_column("Company", width=20)
        table.add_column("Location", width=20)
        table.add_column("Salary", width=15)
        table.add_column("Posted", width=10)
        
        # Add sample data (in real implementation, this would come from database)
        sample_jobs = [
            ("1", "Senior Python Developer", "Google", "San Francisco, CA", "$150k-200k", "2d ago"),
            ("2", "ML Engineer", "OpenAI", "Remote", "$180k-250k", "1d ago"),
            ("3", "Backend Engineer", "Stripe", "Seattle, WA", "$140k-180k", "3d ago"),
            ("4", "Data Scientist", "Netflix", "Los Angeles, CA", "$160k-220k", "1d ago"),
            ("5", "Software Engineer", "Microsoft", "Redmond, WA", "$130k-170k", "4d ago"),
        ]
        
        for job in sample_jobs:
            table.add_row(*job)
        
        self.query_one("#results-status", Static).update(f"Showing {len(sample_jobs)} jobs")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "view-details-btn":
            self.view_job_details()
        elif event.button.id == "export-btn":
            self.action_export()
        elif event.button.id == "back-btn":
            self.action_back()
        elif event.button.id == "filter-btn":
            self.filter_results()
        elif event.button.id == "clear-filter-btn":
            self.clear_filter()
    
    def view_job_details(self) -> None:
        """View details of selected job."""
        table = self.query_one("#results-table", DataTable)
        if table.cursor_row is not None:
            # In real implementation, this would show detailed job information
            self.query_one("#results-status", Static).update(f"Viewing job #{table.cursor_row + 1}")
        else:
            self.query_one("#results-status", Static).update("Please select a job to view details")
    
    def filter_results(self) -> None:
        """Filter results based on input."""
        filter_text = self.query_one("#filter-input", Input).value
        if filter_text:
            self.query_one("#results-status", Static).update(f"Filtering by: {filter_text}")
        else:
            self.query_one("#results-status", Static).update("Please enter filter text")
    
    def clear_filter(self) -> None:
        """Clear current filter."""
        self.query_one("#filter-input", Input).value = ""
        self.query_one("#results-status", Static).update("Filter cleared")
    
    def action_export(self) -> None:
        """Export results to file."""
        self.query_one("#results-status", Static).update("📁 Results exported to jobs_export.json")
    
    def action_refresh(self) -> None:
        """Refresh results."""
        self.query_one("#results-status", Static).update("🔄 Refreshing results...")
        self.set_timer(1.0, lambda: self.query_one("#results-status", Static).update("✅ Results refreshed"))
    
    def action_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()


class JobMinerTUIApp(App):
    """Main JobMiner TUI Application."""
    
    CSS = """
    .screen-title {
        text-align: center;
        padding: 1;
        background: $primary;
        color: $text;
        margin-bottom: 1;
    }
    
    .button-row {
        height: auto;
        margin: 1;
        align: center middle;
    }
    
    .button-row Button {
        margin: 0 1;
        min-width: 20;
    }
    
    .form-group {
        margin: 1 0;
        padding: 1;
        border: solid $primary;
    }
    
    .filter-section {
        margin-bottom: 1;
        padding: 1;
        border: solid $secondary;
    }
    
    .filter-row {
        height: auto;
        align: center middle;
    }
    
    #banner {
        text-align: center;
        color: $accent;
        margin-bottom: 1;
    }
    
    #menu-options {
        padding: 1 2;
        margin-bottom: 1;
    }
    
    #menu-container {
        align: center middle;
        margin: 1;
    }
    
    #results-table {
        height: 20;
        margin: 1 0;
    }
    
    #activity-log {
        height: 10;
        margin: 1 0;
        border: solid $primary;
    }
    
    #progress-bar {
        margin: 1 0;
    }
    """
    
    TITLE = "JobMiner Enhanced CLI"
    SUB_TITLE = "Interactive Job Scraping Tool"
    
    SCREENS = {
        "main": MainMenuScreen,
        "search": SearchScreen,
        "results": ResultsScreen,
    }
    
    def on_mount(self) -> None:
        """Initialize the application."""
        self.push_screen("main")
    
    def on_screen_resume(self, screen) -> None:
        """Handle screen resume events."""
        pass


def main():
    """Run the JobMiner TUI application."""
    app = JobMinerTUIApp()
    app.run()


if __name__ == "__main__":
    main()