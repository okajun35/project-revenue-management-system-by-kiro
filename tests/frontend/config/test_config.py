"""
Frontend testing configuration
"""
import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TestConfig:
    """Configuration for frontend tests"""
    
    # Base URLs
    BASE_URL: str = "http://localhost:5000"
    API_BASE_URL: str = "http://localhost:5000/api"
    
    # Browser settings
    BROWSER_TYPES: List[str] = None
    HEADLESS: bool = True
    BROWSER_TIMEOUT: int = 30000  # milliseconds
    
    # Test data
    TEST_DATABASE_URL: str = "sqlite:///test_frontend.db"
    
    # Report settings
    REPORTS_DIR: str = "tests/frontend/reports"
    SCREENSHOTS_DIR: str = "tests/frontend/reports/screenshots"
    HTML_REPORT_PATH: str = "tests/frontend/reports/html/report.html"
    
    # Template settings
    TEMPLATES_DIR: str = "app/templates"
    
    # Performance thresholds
    PAGE_LOAD_TIMEOUT: int = 10000  # milliseconds
    API_RESPONSE_TIMEOUT: int = 5000  # milliseconds
    
    # Retry settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1000  # milliseconds
    
    def __post_init__(self):
        if self.BROWSER_TYPES is None:
            self.BROWSER_TYPES = ["chromium", "firefox", "webkit"]
        
        # Create directories if they don't exist
        os.makedirs(self.REPORTS_DIR, exist_ok=True)
        os.makedirs(self.SCREENSHOTS_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(self.HTML_REPORT_PATH), exist_ok=True)


# Global test configuration instance
test_config = TestConfig()


# Environment-specific overrides
if os.getenv("CI"):
    test_config.HEADLESS = True
    test_config.BROWSER_TYPES = ["chromium"]  # Use only chromium in CI

if os.getenv("TEST_ENV") == "local":
    test_config.HEADLESS = False
    test_config.BASE_URL = "http://localhost:5000"

if os.getenv("TEST_BROWSER"):
    test_config.BROWSER_TYPES = [os.getenv("TEST_BROWSER")]