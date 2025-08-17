#!/usr/bin/env python3
"""
Simple template test to verify AdminLTE integration works
"""
import os
import sys
from pathlib import Path

def test_template_files():
    """Test that all required template files exist"""
    template_dir = Path("app/templates")
    
    required_files = [
        "base.html",
        "dashboard.html",
        "components/navbar.html",
        "components/sidebar.html"
    ]
    
    print("Testing template files...")
    for file_path in required_files:
        full_path = template_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            return False
    
    return True

def test_adminlte_files():
    """Test that AdminLTE files are properly placed"""
    static_dir = Path("static/AdminLTE-3.2.0")
    
    required_dirs = [
        "dist/css",
        "dist/js", 
        "plugins/jquery",
        "plugins/bootstrap",
        "plugins/fontawesome-free"
    ]
    
    print("\nTesting AdminLTE files...")
    for dir_path in required_dirs:
        full_path = static_dir / dir_path
        if full_path.exists():
            print(f"✓ {dir_path} exists")
        else:
            print(f"✗ {dir_path} missing")
            return False
    
    return True

def test_template_syntax():
    """Basic syntax check for templates"""
    print("\nTesting template syntax...")
    
    # Test base.html
    base_path = Path("app/templates/base.html")
    if base_path.exists():
        content = base_path.read_text(encoding='utf-8')
        if "{% block content %}{% endblock %}" in content:
            print("✓ base.html has content block")
        else:
            print("✗ base.html missing content block")
            return False
            
        if "AdminLTE-3.2.0" in content:
            print("✓ base.html references AdminLTE files")
        else:
            print("✗ base.html missing AdminLTE references")
            return False
    
    # Test dashboard.html
    dashboard_path = Path("app/templates/dashboard.html")
    if dashboard_path.exists():
        content = dashboard_path.read_text(encoding='utf-8')
        if "{% extends \"base.html\" %}" in content:
            print("✓ dashboard.html extends base template")
        else:
            print("✗ dashboard.html doesn't extend base template")
            return False
    
    return True

if __name__ == "__main__":
    print("AdminLTE Template Integration Test")
    print("=" * 40)
    
    success = True
    success &= test_template_files()
    success &= test_adminlte_files()
    success &= test_template_syntax()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! AdminLTE integration is ready.")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Please check the output above.")
        sys.exit(1)