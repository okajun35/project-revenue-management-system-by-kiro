#!/usr/bin/env python3
"""
Manual test for Excel import functionality
"""
import tempfile
import pandas as pd
import os
from app.services.import_service import ImportService

def test_excel_basic_functionality():
    """Test basic Excel functionality"""
    print("Testing Excel import functionality...")
    
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
        service = ImportService()
        
        # Test 1: Excel info retrieval
        print("1. Testing Excel info retrieval...")
        excel_info = service.get_excel_sheets(temp_file.name)
        print(f"   Result: {excel_info}")
        assert excel_info['success'] is True
        assert excel_info['sheet_count'] == 1
        print("   ✓ Excel info retrieval works")
        
        # Test 2: File validation
        print("2. Testing file validation...")
        validation_result = service.validate_file(temp_file.name, 'excel')
        print(f"   Result: {validation_result}")
        assert validation_result['success'] is True
        print("   ✓ File validation works")
        
        # Test 3: Sheet validation
        print("3. Testing sheet validation...")
        sheet_result = service.validate_excel_sheet(temp_file.name, 'TestSheet')
        print(f"   Result: {sheet_result}")
        assert sheet_result['success'] is True
        print("   ✓ Sheet validation works")
        
        print("\n✅ All Excel functionality tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            os.unlink(temp_file.name)
        except:
            pass

def test_excel_multiple_sheets():
    """Test Excel with multiple sheets"""
    print("\nTesting Excel with multiple sheets...")
    
    # Create test Excel file with multiple sheets
    sheet1_data = [{
        'プロジェクトコード': 'EXCEL001',
        'プロジェクト名': 'シート1プロジェクト',
        '支社名': 'テスト支社'
    }]
    
    sheet2_data = [{
        'プロジェクトコード': 'EXCEL002',
        'プロジェクト名': 'シート2プロジェクト',
        '支社名': 'テスト支社'
    }]
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    
    with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
        pd.DataFrame(sheet1_data).to_excel(writer, sheet_name='データシート1', index=False)
        pd.DataFrame(sheet2_data).to_excel(writer, sheet_name='データシート2', index=False)
        pd.DataFrame().to_excel(writer, sheet_name='空シート', index=False)
    
    try:
        service = ImportService()
        
        # Test multiple sheets info
        excel_info = service.get_excel_sheets(temp_file.name)
        print(f"Excel info: {excel_info}")
        assert excel_info['success'] is True
        assert excel_info['sheet_count'] == 3
        
        # Check data sheets
        data_sheets = [sheet for sheet in excel_info['sheets'] if sheet['has_data']]
        print(f"Data sheets: {len(data_sheets)}")
        
        # Test specific sheet validation
        sheet_result = service.validate_excel_sheet(temp_file.name, 'データシート1')
        print(f"Sheet validation: {sheet_result}")
        assert sheet_result['success'] is True
        
        print("✅ Multiple sheets test passed!")
        
    except Exception as e:
        print(f"❌ Multiple sheets test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            os.unlink(temp_file.name)
        except:
            pass

if __name__ == '__main__':
    test_excel_basic_functionality()
    test_excel_multiple_sheets()
    print("\n🎉 All manual tests completed!")