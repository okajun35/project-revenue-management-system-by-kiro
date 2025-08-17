"""
Template integration testing module

This module provides comprehensive template testing functionality including:
- Template rendering validation
- HTML structure verification
- JavaScript block inclusion testing
- CSS block inclusion testing
- Template inheritance validation
"""

from .template_integration_tester import (
    TemplateIntegrationTester,
    PageRenderResult,
    JSInclusionResult,
    CSSInclusionResult,
    TemplateBlockResult
)

__all__ = [
    'TemplateIntegrationTester',
    'PageRenderResult',
    'JSInclusionResult', 
    'CSSInclusionResult',
    'TemplateBlockResult'
]