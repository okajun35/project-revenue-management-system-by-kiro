#!/usr/bin/env python3
"""
CSVインポート機能のテスト
"""
import sys
import os
import tempfile
from io import StringIO

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_csv_import():
    """Test CSV import functionality"""
    from app import create_app, db
    from app.models import Project, Branch
    from app.services.import_service import ImportService
    
    # Create Flask app
    app = create_app('testing')
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("=== CSVインポート機能テスト ===")
        
        # Test 1: Check if ImportService can be imported
        import_service = ImportService()
        print("✓ ImportService imported successfully")
            
        # Test 2: Check if pandas is available
        import pandas as pd
        print("✓ pandas library is available")
            
            # Test 3: Test CSV file validation
            print("\n--- CSV File Validation Test ---")
            
            # Create a test CSV file
            csv_content = """プロジェクトコード,プロジェクト名,支社名,売上の年度,受注角度,売上（契約金）,経費（トータル）
PROJ-TEST-001,テストプロジェクト1,テスト支社,2024,〇,1000000,800000
PROJ-TEST-002,テストプロジェクト2,テスト支社,2024,△,2000000,1500000"""
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
                f.write(csv_content)
                temp_csv_path = f.name
            
            try:
                # Test file validation
                result = import_service.validate_file(temp_csv_path, 'csv')
                
                assert result['success'], f"CSV validation failed: {result.get('error', 'Unknown error')}"
                print(f"✓ CSV validation successful: {result['row_count']} rows found")
                print(f"  Columns: {result['columns']}")
                
                # Test 4: Test preview data
                print("\n--- Preview Data Test ---")
                preview_result = import_service.get_preview_data(temp_csv_path, 'csv')
                
                assert preview_result['success'], f"Preview data failed: {preview_result.get('error', 'Unknown error')}"
                print(f"✓ Preview data retrieved: {len(preview_result['data'])} rows")
                for i, row in enumerate(preview_result['data']):
                    print(f"  Row {i+1}: {row.get('project_code', 'N/A')} - {row.get('project_name', 'N/A')}")
                
                # Test 5: Test import execution
                print("\n--- Import Execution Test ---")
                
                # Check initial project count
                initial_count = Project.query.count()
                print(f"Initial project count: {initial_count}")
                
                # Execute import
                import_result = import_service.execute_import(temp_csv_path, 'csv')
                
                assert import_result['success'], f"Import execution failed: {import_result.get('error', 'Unknown error')}"
                print(f"✓ Import executed successfully")
                print(f"  Success: {import_result['success_count']} projects")
                print(f"  Errors: {import_result['error_count']} projects")
                
                if import_result['error_count'] > 0:
                    print("  Error details:")
                    for error in import_result.get('errors', []):
                        print(f"    Row {error['row']}: {error['error']}")
                
                # Check final project count
                final_count = Project.query.count()
                print(f"Final project count: {final_count}")
                
                assert final_count > initial_count, "No projects were added to database"
                print("✓ Projects were successfully added to database")
                
                # Display imported projects
                imported_projects = Project.query.filter(
                    Project.project_code.like('PROJ-TEST-%')
                ).all()
                
                print("\nImported projects:")
                for project in imported_projects:
                    print(f"  - {project.project_code}: {project.project_name}")
                    print(f"    Branch: {project.branch.branch_name if project.branch else 'N/A'}")
                    print(f"    Revenue: {project.revenue}, Expenses: {project.expenses}")
                    print(f"    Gross Profit: {project.gross_profit}")
                
            # Test 6: Test branch creation
            print("\n--- Branch Creation Test ---")
            test_branch = Branch.query.filter_by(branch_name='テスト支社').first()
            assert test_branch is not None, "Branch was not created"
            print(f"✓ Branch created successfully: {test_branch.branch_code} - {test_branch.branch_name}")
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
        
        print("\n=== All tests passed! ===")

if __name__ == '__main__':
    success = test_csv_import()
    sys.exit(0 if success else 1)