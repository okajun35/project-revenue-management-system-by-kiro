#!/usr/bin/env python3
"""
Manual test for Excel import routes
"""
import tempfile
import pandas as pd
import os
from app import create_app, db
from app.models import Project, Branch

def test_excel_routes():
    """Test Excel import routes"""
    print("Testing Excel import routes...")
    
    # Create Flask app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
    
    with app.app_context():
        db.create_all()
        
        # Create test Excel file
        test_data = [{
            'プロジェクトコード': 'EXCEL001',
            'プロジェクト名': 'テストプロジェクト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '〇',
            '売上': 1000000,
            '経費': 800000
        }]
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        
        with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
            pd.DataFrame(test_data).to_excel(writer, sheet_name='TestSheet', index=False)
        
        try:
            client = app.test_client()
            
            # Test 1: Upload Excel file
            print("1. Testing Excel file upload...")
            with open(temp_file.name, 'rb') as f:
                response = client.post('/import/upload', data={
                    'file': (f, 'test.xlsx'),
                    'file_type': 'excel'
                }, follow_redirects=False)
            
            print(f"   Upload response status: {response.status_code}")
            if response.status_code == 302:
                print("   ✓ File upload successful (redirected)")
            else:
                print(f"   Response data: {response.get_data(as_text=True)}")
            
            # Test 2: Access mapping page
            print("2. Testing mapping page access...")
            with client.session_transaction() as sess:
                # Simulate session data
                sess['import_file'] = temp_file.name
                sess['import_type'] = 'excel'
                sess['import_columns'] = ['プロジェクトコード', 'プロジェクト名', '支社名', '売上の年度', '受注角度', '売上', '経費']
                sess['import_sample_data'] = test_data
                sess['import_row_count'] = 1
                sess['selected_sheet'] = 'TestSheet'
            
            response = client.get('/import/mapping')
            print(f"   Mapping page status: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ Mapping page accessible")
            else:
                print(f"   Error: {response.get_data(as_text=True)}")
            
            print("✅ Excel routes test completed!")
            
        except Exception as e:
            print(f"❌ Routes test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass

if __name__ == '__main__':
    test_excel_routes()
    print("\n🎉 Route tests completed!")