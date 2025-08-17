"""
Template Integration Tester

This module provides the TemplateIntegrationTester class for testing template rendering,
HTML generation, and JavaScript/CSS block inclusion.
"""
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup
from flask import Flask
from flask.testing import FlaskClient


@dataclass
class PageRenderResult:
    """Result of page rendering test"""
    success: bool
    status_code: int
    content_length: int
    render_time: float
    error_message: Optional[str] = None
    html_content: Optional[str] = None


@dataclass
class JSInclusionResult:
    """Result of JavaScript inclusion test"""
    success: bool
    script_tags_found: int
    inline_scripts_found: int
    external_scripts_found: int
    expected_scripts: List[str]
    missing_scripts: List[str]
    error_message: Optional[str] = None


@dataclass
class CSSInclusionResult:
    """Result of CSS inclusion test"""
    success: bool
    style_tags_found: int
    link_tags_found: int
    inline_styles_found: int
    expected_styles: List[str]
    missing_styles: List[str]
    error_message: Optional[str] = None


@dataclass
class TemplateBlockResult:
    """Result of template block validation"""
    success: bool
    blocks_found: List[str]
    expected_blocks: List[str]
    missing_blocks: List[str]
    extra_blocks: List[str]
    error_message: Optional[str] = None


class TemplateIntegrationTester:
    """
    Template integration tester for validating template rendering,
    HTML generation, and JavaScript/CSS block inclusion.
    """
    
    def __init__(self, app: Flask, client: FlaskClient):
        """
        Initialize the template integration tester.
        
        Args:
            app: Flask application instance
            client: Flask test client
        """
        self.app = app
        self.client = client
        
        # Expected JavaScript libraries/files for different pages
        self.expected_js = {
            'dashboard': [
                'jquery',
                'bootstrap',
                'adminlte',
                'chart.js'
            ],
            'projects': [
                'jquery',
                'bootstrap',
                'adminlte',
                'datatables'
            ],
            'branches': [
                'jquery',
                'bootstrap',
                'adminlte',
                'datatables'
            ],
            'import': [
                'jquery',
                'bootstrap',
                'adminlte'
            ]
        }
        
        # Expected CSS files for different pages
        self.expected_css = {
            'dashboard': [
                'bootstrap',
                'adminlte',
                'fontawesome'
            ],
            'projects': [
                'bootstrap',
                'adminlte',
                'fontawesome',
                'datatables'
            ],
            'branches': [
                'bootstrap',
                'adminlte',
                'fontawesome',
                'datatables'
            ],
            'import': [
                'bootstrap',
                'adminlte',
                'fontawesome'
            ]
        }
        
        # Expected template blocks for different page types
        self.expected_blocks = {
            'base': ['title', 'content', 'scripts', 'styles'],
            'dashboard': ['title', 'content', 'scripts'],
            'list_page': ['title', 'content', 'scripts'],
            'form_page': ['title', 'content', 'scripts'],
            'detail_page': ['title', 'content', 'scripts']
        }

    def test_page_rendering(self, url: str, expected_status: int = 200) -> PageRenderResult:
        """
        Test page rendering and basic HTML generation.
        
        Args:
            url: URL to test
            expected_status: Expected HTTP status code
            
        Returns:
            PageRenderResult with test results
        """
        import time
        
        try:
            start_time = time.time()
            response = self.client.get(url)
            render_time = time.time() - start_time
            
            success = response.status_code == expected_status
            error_message = None
            
            if not success:
                error_message = f"Expected status {expected_status}, got {response.status_code}"
            
            # Basic HTML validation
            if success and response.data:
                html_content = response.data.decode('utf-8')
                
                # Check for basic HTML structure
                if not self._validate_basic_html_structure(html_content):
                    success = False
                    error_message = "Invalid HTML structure detected"
            else:
                html_content = None
            
            return PageRenderResult(
                success=success,
                status_code=response.status_code,
                content_length=len(response.data) if response.data else 0,
                render_time=render_time,
                error_message=error_message,
                html_content=html_content
            )
            
        except Exception as e:
            return PageRenderResult(
                success=False,
                status_code=0,
                content_length=0,
                render_time=0.0,
                error_message=str(e)
            )

    def test_javascript_inclusion(self, url: str, page_type: str = 'default') -> JSInclusionResult:
        """
        Test JavaScript block inclusion and script tags.
        
        Args:
            url: URL to test
            page_type: Type of page (dashboard, projects, branches, etc.)
            
        Returns:
            JSInclusionResult with test results
        """
        try:
            response = self.client.get(url)
            
            if response.status_code != 200:
                return JSInclusionResult(
                    success=False,
                    script_tags_found=0,
                    inline_scripts_found=0,
                    external_scripts_found=0,
                    expected_scripts=[],
                    missing_scripts=[],
                    error_message=f"Failed to load page: {response.status_code}"
                )
            
            html_content = response.data.decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all script tags
            script_tags = soup.find_all('script')
            script_tags_found = len(script_tags)
            
            # Count inline vs external scripts
            inline_scripts = [tag for tag in script_tags if not tag.get('src')]
            external_scripts = [tag for tag in script_tags if tag.get('src')]
            
            inline_scripts_found = len(inline_scripts)
            external_scripts_found = len(external_scripts)
            
            # Get expected scripts for this page type
            expected_scripts = self.expected_js.get(page_type, [])
            
            # Check which expected scripts are missing
            missing_scripts = []
            for expected_script in expected_scripts:
                found = False
                for script_tag in script_tags:
                    src = script_tag.get('src', '')
                    script_content = script_tag.string or ''
                    
                    if (expected_script.lower() in src.lower() or 
                        expected_script.lower() in script_content.lower()):
                        found = True
                        break
                
                if not found:
                    missing_scripts.append(expected_script)
            
            success = len(missing_scripts) == 0 and script_tags_found > 0
            error_message = None
            
            if missing_scripts:
                error_message = f"Missing expected scripts: {', '.join(missing_scripts)}"
            elif script_tags_found == 0:
                error_message = "No script tags found"
            
            return JSInclusionResult(
                success=success,
                script_tags_found=script_tags_found,
                inline_scripts_found=inline_scripts_found,
                external_scripts_found=external_scripts_found,
                expected_scripts=expected_scripts,
                missing_scripts=missing_scripts,
                error_message=error_message
            )
            
        except Exception as e:
            return JSInclusionResult(
                success=False,
                script_tags_found=0,
                inline_scripts_found=0,
                external_scripts_found=0,
                expected_scripts=[],
                missing_scripts=[],
                error_message=str(e)
            )

    def test_css_inclusion(self, url: str, page_type: str = 'default') -> CSSInclusionResult:
        """
        Test CSS block inclusion and style tags.
        
        Args:
            url: URL to test
            page_type: Type of page (dashboard, projects, branches, etc.)
            
        Returns:
            CSSInclusionResult with test results
        """
        try:
            response = self.client.get(url)
            
            if response.status_code != 200:
                return CSSInclusionResult(
                    success=False,
                    style_tags_found=0,
                    link_tags_found=0,
                    inline_styles_found=0,
                    expected_styles=[],
                    missing_styles=[],
                    error_message=f"Failed to load page: {response.status_code}"
                )
            
            html_content = response.data.decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find style and link tags
            style_tags = soup.find_all('style')
            link_tags = soup.find_all('link', rel='stylesheet')
            
            style_tags_found = len(style_tags)
            link_tags_found = len(link_tags)
            inline_styles_found = len([tag for tag in soup.find_all() if tag.get('style')])
            
            # Get expected styles for this page type
            expected_styles = self.expected_css.get(page_type, [])
            
            # Check which expected styles are missing
            missing_styles = []
            for expected_style in expected_styles:
                found = False
                
                # Check link tags
                for link_tag in link_tags:
                    href = link_tag.get('href', '')
                    if expected_style.lower() in href.lower():
                        found = True
                        break
                
                # Check style tags if not found in links
                if not found:
                    for style_tag in style_tags:
                        style_content = style_tag.string or ''
                        if expected_style.lower() in style_content.lower():
                            found = True
                            break
                
                if not found:
                    missing_styles.append(expected_style)
            
            success = len(missing_styles) == 0 and (style_tags_found > 0 or link_tags_found > 0)
            error_message = None
            
            if missing_styles:
                error_message = f"Missing expected styles: {', '.join(missing_styles)}"
            elif style_tags_found == 0 and link_tags_found == 0:
                error_message = "No style or link tags found"
            
            return CSSInclusionResult(
                success=success,
                style_tags_found=style_tags_found,
                link_tags_found=link_tags_found,
                inline_styles_found=inline_styles_found,
                expected_styles=expected_styles,
                missing_styles=missing_styles,
                error_message=error_message
            )
            
        except Exception as e:
            return CSSInclusionResult(
                success=False,
                style_tags_found=0,
                link_tags_found=0,
                inline_styles_found=0,
                expected_styles=[],
                missing_styles=[],
                error_message=str(e)
            )

    def test_template_blocks(self, url: str, page_type: str = 'default') -> TemplateBlockResult:
        """
        Test template block structure and inheritance.
        
        Args:
            url: URL to test
            page_type: Type of page template
            
        Returns:
            TemplateBlockResult with test results
        """
        try:
            response = self.client.get(url)
            
            if response.status_code != 200:
                return TemplateBlockResult(
                    success=False,
                    blocks_found=[],
                    expected_blocks=[],
                    missing_blocks=[],
                    extra_blocks=[],
                    error_message=f"Failed to load page: {response.status_code}"
                )
            
            html_content = response.data.decode('utf-8')
            
            # Extract block indicators from HTML comments or structure
            blocks_found = self._extract_template_blocks(html_content)
            expected_blocks = self.expected_blocks.get(page_type, [])
            
            missing_blocks = [block for block in expected_blocks if block not in blocks_found]
            extra_blocks = [block for block in blocks_found if block not in expected_blocks]
            
            success = len(missing_blocks) == 0
            error_message = None
            
            if missing_blocks:
                error_message = f"Missing template blocks: {', '.join(missing_blocks)}"
            
            return TemplateBlockResult(
                success=success,
                blocks_found=blocks_found,
                expected_blocks=expected_blocks,
                missing_blocks=missing_blocks,
                extra_blocks=extra_blocks,
                error_message=error_message
            )
            
        except Exception as e:
            return TemplateBlockResult(
                success=False,
                blocks_found=[],
                expected_blocks=[],
                missing_blocks=[],
                extra_blocks=[],
                error_message=str(e)
            )

    def test_comprehensive_page(self, url: str, page_type: str = 'default') -> Dict[str, Any]:
        """
        Run comprehensive tests on a page including rendering, JS, CSS, and blocks.
        
        Args:
            url: URL to test
            page_type: Type of page
            
        Returns:
            Dictionary with all test results
        """
        results = {
            'url': url,
            'page_type': page_type,
            'render_result': self.test_page_rendering(url),
            'js_result': self.test_javascript_inclusion(url, page_type),
            'css_result': self.test_css_inclusion(url, page_type),
            'blocks_result': self.test_template_blocks(url, page_type)
        }
        
        # Overall success
        results['overall_success'] = all([
            results['render_result'].success,
            results['js_result'].success,
            results['css_result'].success,
            results['blocks_result'].success
        ])
        
        return results

    def _validate_basic_html_structure(self, html_content: str) -> bool:
        """
        Validate basic HTML structure.
        
        Args:
            html_content: HTML content to validate
            
        Returns:
            True if valid HTML structure
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check for basic HTML elements
            has_html = soup.find('html') is not None
            has_head = soup.find('head') is not None
            has_body = soup.find('body') is not None
            has_title = soup.find('title') is not None
            
            return has_html and has_head and has_body and has_title
            
        except Exception:
            return False

    def _extract_template_blocks(self, html_content: str) -> List[str]:
        """
        Extract template block indicators from HTML content.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            List of detected template blocks
        """
        blocks_found = []
        
        # Look for common block indicators
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for title block
        if soup.find('title'):
            blocks_found.append('title')
        
        # Check for content block (main content area)
        content_indicators = [
            soup.find('main'),
            soup.find(class_=re.compile(r'content|main')),
            soup.find(id=re.compile(r'content|main'))
        ]
        if any(content_indicators):
            blocks_found.append('content')
        
        # Check for scripts block
        if soup.find_all('script'):
            blocks_found.append('scripts')
        
        # Check for styles block
        if soup.find_all('style') or soup.find_all('link', rel='stylesheet'):
            blocks_found.append('styles')
        
        # Look for HTML comments that might indicate blocks
        comments = soup.find_all(string=lambda text: isinstance(text, str) and 
                                 text.strip().startswith('<!--') and 'block' in text.lower())
        
        for comment in comments:
            # Extract block names from comments like <!-- block content -->
            block_match = re.search(r'block\s+(\w+)', comment.lower())
            if block_match:
                block_name = block_match.group(1)
                if block_name not in blocks_found:
                    blocks_found.append(block_name)
        
        return blocks_found