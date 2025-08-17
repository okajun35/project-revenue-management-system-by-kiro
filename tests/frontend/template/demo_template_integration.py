#!/usr/bin/env python3
"""
Demo script for Template Integration Tester

This script demonstrates how to use the TemplateIntegrationTester class
to test template rendering, JavaScript inclusion, CSS inclusion, and template blocks.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app import create_app
from tests.frontend.template.template_integration_tester import TemplateIntegrationTester


def main():
    """Run template integration tests demo"""
    print("=== Template Integration Tester Demo ===\n")
    
    # Create Flask app for testing
    app = create_app('testing')
    
    with app.app_context():
        # Create test client
        client = app.test_client()
        
        # Initialize the tester
        tester = TemplateIntegrationTester(app, client)
        
        # Test pages
        pages_to_test = [
            ('/', 'dashboard', 'Dashboard'),
            ('/projects/', 'projects', 'Projects List'),
            ('/branches/', 'branches', 'Branches List')
        ]
        
        for url, page_type, page_name in pages_to_test:
            print(f"Testing {page_name} ({url})...")
            print("-" * 50)
            
            # Test page rendering
            render_result = tester.test_page_rendering(url)
            print(f"✓ Page Rendering: {'PASS' if render_result.success else 'FAIL'}")
            if render_result.success:
                print(f"  - Status Code: {render_result.status_code}")
                print(f"  - Content Length: {render_result.content_length} bytes")
                print(f"  - Render Time: {render_result.render_time:.3f}s")
            else:
                print(f"  - Error: {render_result.error_message}")
            
            # Test JavaScript inclusion
            js_result = tester.test_javascript_inclusion(url, page_type)
            print(f"✓ JavaScript Inclusion: {'PASS' if js_result.success else 'FAIL'}")
            print(f"  - Script Tags Found: {js_result.script_tags_found}")
            print(f"  - Inline Scripts: {js_result.inline_scripts_found}")
            print(f"  - External Scripts: {js_result.external_scripts_found}")
            if js_result.missing_scripts:
                print(f"  - Missing Scripts: {', '.join(js_result.missing_scripts)}")
            
            # Test CSS inclusion
            css_result = tester.test_css_inclusion(url, page_type)
            print(f"✓ CSS Inclusion: {'PASS' if css_result.success else 'FAIL'}")
            print(f"  - Style Tags Found: {css_result.style_tags_found}")
            print(f"  - Link Tags Found: {css_result.link_tags_found}")
            print(f"  - Inline Styles Found: {css_result.inline_styles_found}")
            if css_result.missing_styles:
                print(f"  - Missing Styles: {', '.join(css_result.missing_styles)}")
            
            # Test template blocks
            blocks_result = tester.test_template_blocks(url, page_type)
            print(f"✓ Template Blocks: {'PASS' if blocks_result.success else 'FAIL'}")
            print(f"  - Blocks Found: {', '.join(blocks_result.blocks_found)}")
            if blocks_result.missing_blocks:
                print(f"  - Missing Blocks: {', '.join(blocks_result.missing_blocks)}")
            
            # Comprehensive test
            comprehensive_result = tester.test_comprehensive_page(url, page_type)
            print(f"✓ Overall Result: {'PASS' if comprehensive_result['overall_success'] else 'FAIL'}")
            
            print("\n")
        
        print("=== Demo Complete ===")
        print("\nThe TemplateIntegrationTester provides comprehensive testing for:")
        print("- Template rendering and HTML generation")
        print("- JavaScript block inclusion and script validation")
        print("- CSS block inclusion and style validation")
        print("- Template block structure and inheritance")
        print("- Performance measurement")
        print("- Error detection and reporting")


if __name__ == '__main__':
    main()