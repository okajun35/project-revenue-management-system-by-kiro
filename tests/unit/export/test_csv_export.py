#!/usr/bin/env python3
"""
CSV Export Functionality Test Script
"""

import requests
import json
import sys
import os

def test_csv_export():
    """Test CSV export functionality"""
    base_url = "http://localhost:5000"
    
    print("Testing CSV Export Functionality...")
    print("=" * 50)
    
    # Test 1: Preview API
    print("\n1. Testing Export Preview API...")
    try:
        response = requests.get(f"{base_url}/export/preview")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Total Count: {data.get('total_count')}")
            print(f"Preview Count: {data.get('preview_count')}")
            print("✅ Preview API working")
        else:
            print(f"❌ Preview API failed: {response.text}")
    except Exception as e:
        print(f"❌ Preview API error: {e}")
    
    # Test 2: CSV Download Link API
    print("\n2. Testing CSV Download Link API...")
    try:
        response = requests.get(f"{base_url}/export/csv/download-link")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Record Count: {data.get('record_count')}")
            print(f"Download URL: {data.get('download_url')}")
            print("✅ Download Link API working")
        else:
            print(f"❌ Download Link API failed: {response.text}")
    except Exception as e:
        print(f"❌ Download Link API error: {e}")
    
    # Test 3: CSV Export with filters
    print("\n3. Testing CSV Export with filters...")
    try:
        params = {
            'fiscal_year': '2024',
            'project_code': 'TEST'
        }
        response = requests.get(f"{base_url}/export/preview", params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Filtered Total Count: {data.get('total_count')}")
            print("✅ Filtered export working")
        else:
            print(f"❌ Filtered export failed: {response.text}")
    except Exception as e:
        print(f"❌ Filtered export error: {e}")
    
    # Test 4: Check if pandas is working
    print("\n4. Testing pandas import...")
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        # Create a simple DataFrame to test
        df = pd.DataFrame({
            'test_col1': ['value1', 'value2'],
            'test_col2': [1, 2]
        })
        print(f"✅ DataFrame created: {len(df)} rows")
        
        # Test CSV generation
        import io
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        csv_content = output.getvalue()
        print(f"✅ CSV generation working: {len(csv_content)} characters")
        
    except Exception as e:
        print(f"❌ Pandas test error: {e}")
    
    print("\n" + "=" * 50)
    print("CSV Export Test Complete!")

if __name__ == "__main__":
    test_csv_export()