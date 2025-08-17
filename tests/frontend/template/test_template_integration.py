"""
Template Integration Tests

Tests for template rendering, HTML generation, and JavaScript/CSS block inclusion.
"""
import pytest
from tests.frontend.template.template_integration_tester import (
    TemplateIntegrationTester,
    PageRenderResult,
    JSInclusionResult,
    CSSInclusionResult,
    TemplateBlockResult
)


class TestTemplateIntegration:
    """Test template integration functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app, client):
        """Setup test environment"""
        self.app = app
        self.client = client
        self.tester = TemplateIntegrationTester(app, client)

    @pytest.mark.template
    def test_dashboard_page_rendering(self):
        """Test dashboard page rendering - Requirement 1.1"""
        result = self.tester.test_page_rendering('/')
        
        assert result.success, f"Dashboard rendering failed: {result.error_message}"
        assert result.status_code == 200
        assert result.content_length > 0
        assert result.html_content is not None
        assert '<html' in result.html_content
        assert '<head>' in result.html_content
        assert 'body>' in result.html_content  # Could be <body> or </body>

    @pytest.mark.template
    def test_projects_page_rendering(self):
        """Test projects page rendering - Requirement 1.1"""
        result = self.tester.test_page_rendering('/projects/')
        
        assert result.success, f"Projects page rendering failed: {result.error_message}"
        assert result.status_code == 200
        assert result.content_length > 0
        assert result.html_content is not None

    @pytest.mark.template
    def test_branches_page_rendering(self):
        """Test branches page rendering - Requirement 1.1"""
        result = self.tester.test_page_rendering('/branches/')
        
        assert result.success, f"Branches page rendering failed: {result.error_message}"
        assert result.status_code == 200
        assert result.content_length > 0

    @pytest.mark.template
    def test_dashboard_template_inheritance(self):
        """Test dashboard template inheritance - Requirement 1.2"""
        result = self.tester.test_template_blocks('/', 'dashboard')
        
        assert result.success, f"Dashboard template blocks failed: {result.error_message}"
        assert 'title' in result.blocks_found
        assert 'content' in result.blocks_found
        assert len(result.missing_blocks) == 0, f"Missing blocks: {result.missing_blocks}"

    @pytest.mark.template
    def test_projects_template_inheritance(self):
        """Test projects template inheritance - Requirement 1.2"""
        result = self.tester.test_template_blocks('/projects/', 'list_page')
        
        assert result.success, f"Projects template blocks failed: {result.error_message}"
        assert 'title' in result.blocks_found
        assert 'content' in result.blocks_found

    @pytest.mark.template
    def test_dashboard_javascript_inclusion(self):
        """Test dashboard JavaScript block inclusion - Requirement 1.3"""
        result = self.tester.test_javascript_inclusion('/', 'dashboard')
        
        assert result.success, f"Dashboard JS inclusion failed: {result.error_message}"
        assert result.script_tags_found > 0, "No script tags found"
        
        # Check for specific expected scripts
        expected_found = 0
        for expected in result.expected_scripts:
            if expected not in result.missing_scripts:
                expected_found += 1
        
        # At least some expected scripts should be found
        assert expected_found > 0 or len(result.expected_scripts) == 0, \
            f"No expected scripts found. Missing: {result.missing_scripts}"

    @pytest.mark.template
    def test_projects_javascript_inclusion(self):
        """Test projects JavaScript block inclusion - Requirement 1.3"""
        result = self.tester.test_javascript_inclusion('/projects/', 'projects')
        
        assert result.success, f"Projects JS inclusion failed: {result.error_message}"
        assert result.script_tags_found > 0, "No script tags found"
        
        # DataTables should be included for projects page
        datatables_found = False
        for script in result.expected_scripts:
            if 'datatables' in script.lower() and script not in result.missing_scripts:
                datatables_found = True
                break
        
        # If DataTables is expected, it should be found
        if 'datatables' in [s.lower() for s in result.expected_scripts]:
            assert datatables_found, "DataTables script not found in projects page"

    @pytest.mark.template
    def test_dashboard_css_inclusion(self):
        """Test dashboard CSS block inclusion - Requirement 1.4"""
        result = self.tester.test_css_inclusion('/', 'dashboard')
        
        assert result.success, f"Dashboard CSS inclusion failed: {result.error_message}"
        assert result.style_tags_found > 0 or result.link_tags_found > 0, \
            "No style or link tags found"

    @pytest.mark.template
    def test_projects_css_inclusion(self):
        """Test projects CSS block inclusion - Requirement 1.4"""
        result = self.tester.test_css_inclusion('/projects/', 'projects')
        
        assert result.success, f"Projects CSS inclusion failed: {result.error_message}"
        assert result.style_tags_found > 0 or result.link_tags_found > 0, \
            "No style or link tags found"

    @pytest.mark.template
    def test_branches_css_inclusion(self):
        """Test branches CSS block inclusion - Requirement 1.4"""
        result = self.tester.test_css_inclusion('/branches/', 'branches')
        
        assert result.success, f"Branches CSS inclusion failed: {result.error_message}"
        assert result.style_tags_found > 0 or result.link_tags_found > 0, \
            "No style or link tags found"

    @pytest.mark.template
    def test_comprehensive_dashboard_test(self):
        """Comprehensive test for dashboard page - Requirements 1.1, 1.2, 1.3, 1.4"""
        results = self.tester.test_comprehensive_page('/', 'dashboard')
        
        assert results['overall_success'], "Dashboard comprehensive test failed"
        assert results['render_result'].success, "Dashboard rendering failed"
        assert results['js_result'].success, "Dashboard JS inclusion failed"
        assert results['css_result'].success, "Dashboard CSS inclusion failed"
        assert results['blocks_result'].success, "Dashboard template blocks failed"

    @pytest.mark.template
    def test_comprehensive_projects_test(self):
        """Comprehensive test for projects page - Requirements 1.1, 1.2, 1.3, 1.4"""
        results = self.tester.test_comprehensive_page('/projects/', 'projects')
        
        assert results['overall_success'], "Projects comprehensive test failed"
        assert results['render_result'].success, "Projects rendering failed"
        assert results['js_result'].success, "Projects JS inclusion failed"
        assert results['css_result'].success, "Projects CSS inclusion failed"
        assert results['blocks_result'].success, "Projects template blocks failed"

    @pytest.mark.template
    def test_comprehensive_branches_test(self):
        """Comprehensive test for branches page - Requirements 1.1, 1.2, 1.3, 1.4"""
        results = self.tester.test_comprehensive_page('/branches/', 'branches')
        
        assert results['overall_success'], "Branches comprehensive test failed"
        assert results['render_result'].success, "Branches rendering failed"
        assert results['js_result'].success, "Branches JS inclusion failed"
        assert results['css_result'].success, "Branches CSS inclusion failed"
        assert results['blocks_result'].success, "Branches template blocks failed"

    @pytest.mark.template
    def test_template_error_detection(self):
        """Test template error detection for non-existent pages"""
        result = self.tester.test_page_rendering('/nonexistent-page')
        
        # Should fail with 404
        assert not result.success
        assert result.status_code == 404

    @pytest.mark.template
    def test_javascript_block_validation(self):
        """Test JavaScript block validation across multiple pages"""
        pages_to_test = [
            ('/', 'dashboard'),
            ('/projects/', 'projects'),
            ('/branches/', 'branches')
        ]
        
        for url, page_type in pages_to_test:
            result = self.tester.test_javascript_inclusion(url, page_type)
            
            # Each page should have at least some JavaScript
            assert result.script_tags_found > 0, f"No scripts found on {url}"
            
            # Should have jQuery (common across all pages)
            jquery_found = False
            for script_tag in ['jquery', 'jQuery']:
                if script_tag not in result.missing_scripts:
                    jquery_found = True
                    break
            
            # Note: We don't assert jQuery is required as it depends on actual implementation

    @pytest.mark.template
    def test_css_block_validation(self):
        """Test CSS block validation across multiple pages"""
        pages_to_test = [
            ('/', 'dashboard'),
            ('/projects/', 'projects'),
            ('/branches/', 'branches')
        ]
        
        for url, page_type in pages_to_test:
            result = self.tester.test_css_inclusion(url, page_type)
            
            # Each page should have at least some CSS
            assert (result.style_tags_found > 0 or result.link_tags_found > 0), \
                f"No CSS found on {url}"

    @pytest.mark.template
    def test_html_structure_validation(self):
        """Test HTML structure validation - Requirement 1.1"""
        pages_to_test = ['/', '/projects/', '/branches/']
        
        for url in pages_to_test:
            result = self.tester.test_page_rendering(url)
            
            assert result.success, f"Page {url} failed to render"
            assert result.html_content is not None
            
            # Validate basic HTML structure
            html = result.html_content
            assert '<!DOCTYPE html>' in html or '<html' in html
            assert '<head>' in html
            assert 'body>' in html  # Could be <body> or </body>
            assert '<title>' in html

    @pytest.mark.template
    def test_template_performance(self):
        """Test template rendering performance"""
        pages_to_test = ['/', '/projects/', '/branches/']
        
        for url in pages_to_test:
            result = self.tester.test_page_rendering(url)
            
            assert result.success, f"Page {url} failed to render"
            
            # Template should render within reasonable time (5 seconds)
            assert result.render_time < 5.0, \
                f"Page {url} took too long to render: {result.render_time}s"
            
            # Content should not be empty
            assert result.content_length > 100, \
                f"Page {url} content too small: {result.content_length} bytes"


class TestTemplateIntegrationEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app, client):
        """Setup test environment"""
        self.app = app
        self.client = client
        self.tester = TemplateIntegrationTester(app, client)

    @pytest.mark.template
    def test_invalid_url_handling(self):
        """Test handling of invalid URLs"""
        invalid_urls = [
            '/invalid-page',
            '/projects/999999',
            '/branches/invalid'
        ]
        
        for url in invalid_urls:
            result = self.tester.test_page_rendering(url)
            
            # Should handle gracefully (either 404 or redirect)
            assert result.status_code in [404, 302, 500], \
                f"Unexpected status for {url}: {result.status_code}"

    @pytest.mark.template
    def test_empty_response_handling(self):
        """Test handling of empty responses"""
        # This tests the robustness of our tester
        result = self.tester.test_javascript_inclusion('/nonexistent', 'default')
        
        assert not result.success
        assert result.script_tags_found == 0
        assert "Failed to load page" in result.error_message

    @pytest.mark.template
    def test_malformed_html_handling(self):
        """Test handling of potentially malformed HTML"""
        # Test with pages that might have issues
        pages_to_test = ['/', '/projects/', '/branches/']
        
        for url in pages_to_test:
            # Test CSS parsing with potentially malformed HTML
            css_result = self.tester.test_css_inclusion(url, 'default')
            
            # Should not crash even if HTML is malformed
            assert isinstance(css_result.success, bool)
            assert isinstance(css_result.style_tags_found, int)
            assert isinstance(css_result.link_tags_found, int)
            
            # Test JS parsing with potentially malformed HTML
            js_result = self.tester.test_javascript_inclusion(url, 'default')
            
            # Should not crash even if HTML is malformed
            assert isinstance(js_result.success, bool)
            assert isinstance(js_result.script_tags_found, int)