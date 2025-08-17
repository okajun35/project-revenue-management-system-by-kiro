#!/usr/bin/env python3
"""テンプレートレンダリングのデバッグ"""

from app import create_app
from flask import render_template_string

def test_simple_template():
    app = create_app()
    with app.app_context():
        try:
            # 簡単なテンプレートをテスト
            simple_template = """
            <!DOCTYPE html>
            <html>
            <head><title>Test</title></head>
            <body><h1>検索条件</h1></body>
            </html>
            """
            
            result = render_template_string(simple_template)
            print(f"Simple template length: {len(result)}")
            print(f"Simple template content: {result}")
            
            return result
            
        except Exception as e:
            print(f"Error rendering simple template: {e}")
            import traceback
            traceback.print_exc()
            return None

def test_base_template():
    app = create_app()
    with app.app_context():
        try:
            # base.htmlを直接テスト
            result = render_template_string("""
            {% extends "base.html" %}
            {% block title %}テスト{% endblock %}
            {% block content %}
            <h1>検索条件</h1>
            {% endblock %}
            """)
            
            print(f"Base template length: {len(result)}")
            print(f"Base template first 200 chars: {result[:200]}")
            
            return result
            
        except Exception as e:
            print(f"Error rendering base template: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    print("=== Testing simple template ===")
    test_simple_template()
    
    print("\n=== Testing base template ===")
    test_base_template()