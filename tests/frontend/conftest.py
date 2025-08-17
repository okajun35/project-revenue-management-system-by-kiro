"""
Frontend testing configuration and fixtures
"""
import os
import sys
import pytest
import tempfile
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import create_app
from app.models import db


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    # Use the testing configuration
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        
        # Add some test data
        from app.models import Project, Branch
        
        # Create test branch
        test_branch = Branch(branch_code="TEST01", branch_name="テスト支社")
        db.session.add(test_branch)
        db.session.commit()
        
        # Create test projects
        test_projects = [
            Project(
                project_code="TEST-001",
                project_name="テストプロジェクト1",
                branch_id=test_branch.id,
                fiscal_year=2024,
                order_probability=100,
                revenue=1000000,
                expenses=800000
            ),
            Project(
                project_code="TEST-002",
                project_name="テストプロジェクト2",
                branch_id=test_branch.id,
                fiscal_year=2024,
                order_probability=50,
                revenue=2000000,
                expenses=1500000
            )
        ]
        
        for project in test_projects:
            db.session.add(project)
        
        db.session.commit()
    
    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture(scope="session")
def browser_context_args():
    """Browser context arguments for Playwright."""
    return {
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
        "record_video_dir": "tests/frontend/reports/videos/",
        "record_video_size": {"width": 1280, "height": 720}
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Ensure report directories exist
    reports_dir = "tests/frontend/reports"
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    Path(f"{reports_dir}/screenshots").mkdir(parents=True, exist_ok=True)
    Path(f"{reports_dir}/html").mkdir(parents=True, exist_ok=True)
    Path(f"{reports_dir}/json").mkdir(parents=True, exist_ok=True)
    Path(f"{reports_dir}/junit").mkdir(parents=True, exist_ok=True)
    Path(f"{reports_dir}/videos").mkdir(parents=True, exist_ok=True)
    Path(f"{reports_dir}/coverage").mkdir(parents=True, exist_ok=True)


@pytest.fixture
def test_data():
    """Provide test data for frontend tests."""
    return {
        "projects": [
            {
                "project_code": "TEST-001",
                "project_name": "テストプロジェクト1",
                "fiscal_year": 2024,
                "order_probability": 100,
                "revenue": 1000000,
                "expenses": 800000
            },
            {
                "project_code": "TEST-002",
                "project_name": "テストプロジェクト2",
                "fiscal_year": 2024,
                "order_probability": 50,
                "revenue": 2000000,
                "expenses": 1500000
            }
        ],
        "branches": [
            {
                "branch_code": "TEST01",
                "branch_name": "テスト支社"
            }
        ]
    }


@pytest.fixture
def template_paths():
    """Provide template file paths for testing."""
    templates_dir = Path("app/templates")
    return {
        "base": templates_dir / "base.html",
        "dashboard": templates_dir / "dashboard.html",
        "projects_index": templates_dir / "projects" / "index.html",
        "projects_form": templates_dir / "projects" / "form.html",
        "projects_show": templates_dir / "projects" / "show.html",
        "branches_index": templates_dir / "branches" / "index.html",
        "branches_form": templates_dir / "branches" / "form.html",
        "branches_show": templates_dir / "branches" / "show.html"
    }


# Pytest hooks for better reporting
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "template: mark test as template integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "syntax: mark test as template syntax test"
    )


# HTML report customization (only if pytest-html is available)
try:
    import pytest_html
    
    def pytest_html_report_title(report):
        """Customize HTML report title."""
        report.title = "Frontend Testing Automation Report"

    def pytest_html_results_summary(prefix, summary, postfix):
        """Customize HTML report summary."""
        prefix.extend([
            "<h2>Frontend Testing Automation</h2>",
            "<p>Comprehensive frontend testing including template, API, and E2E tests.</p>"
        ])
except ImportError:
    # pytest-html not available, skip HTML customization
    pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshots on test failure."""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        # Add screenshot path to the report if it's an E2E test
        if hasattr(item, 'funcargs') and 'page' in item.funcargs:
            screenshot_path = f"tests/frontend/reports/screenshots/failed_{item.name}_{call.when}.png"
            try:
                item.funcargs['page'].screenshot(path=screenshot_path)
                rep.extra = getattr(rep, 'extra', [])
                rep.extra.append({
                    'name': 'Screenshot',
                    'path': screenshot_path,
                    'content_type': 'image/png'
                })
            except Exception as e:
                print(f"Failed to capture screenshot: {e}")