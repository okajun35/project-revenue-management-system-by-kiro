#!/usr/bin/env python3
"""
CSVインポート機能の列マッピングテスト
"""
import sys
import os
import tempfile
from io import StringIO

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_csv_import_with_mapping():
    """Test CSV import functionality with column mapping"""
    from app import create_app, db
    from app.models import Project, Branch
    from app.services.import_service import ImportService
    
    # Create Flask app
    app = create_app('testing')
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("=== CSVインポート列マッピング機能テスト ===")
        
        # Test 1: Auto mapping functionality
        print("\n--- Auto Mapping Test ---")
        import_service = ImportService()
            
            # Test with Japanese column names
            japanese_columns = ['プロジェクトコード', 'プロジェクト名', '支社名', '売上の年度', '受注角度', '売上（契約金）', '経費（トータル）']
            auto_mapping = import_service.get_auto_mapping(japanese_columns)
            
            print(f"Japanese columns: {japanese_columns}")
            print(f"Auto mapping result: {auto_mapping}")
            
            expected_mapping = {
                'project_code': 'プロジェクトコード',
                'project_name': 'プロジェクト名',
                'branch_name': '支社名',
                'fiscal_year': '売上の年度',
                'order_probability': '受注角度',
                'revenue': '売上（契約金）',
                'expenses': '経費（トータル）'
            }
            
            for field, expected_column in expected_mapping.items():
                if field in auto_mapping and auto_mapping[field] == expected_column:
                    print(f"✓ {field} -> {expected_column}")
                else:
                    print(f"✗ {field} mapping failed. Expected: {expected_column}, Got: {auto_mapping.get(field, 'None')}")
            
            # Test 2: Custom column mapping
            print("\n--- Custom Column Mapping Test ---")
            
            # Create a CSV with different column names
            csv_content = """Code,Name,Office,Year,Probability,Sales,Cost
PROJ-MAP-001,マッピングテスト1,マッピング支社,2024,100,1500000,1200000
PROJ-MAP-002,マッピングテスト2,マッピング支社,2024,50,2500000,2000000"""
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
                f.write(csv_content)
                temp_csv_path = f.name
            
            try:
                # Test file validation (should work with any column names)
                result = import_service.validate_file(temp_csv_path, 'csv')
                
                assert result['success'], f"CSV validation failed: {result.get('error', 'Unknown error')}"
                print(f"✓ CSV validation successful: {result['row_count']} rows found")
                print(f"  Original columns: {result['columns']}")
                
                # Test custom column mapping
                custom_mapping = {
                    'project_code': 'Code',
                    'project_name': 'Name',
                    'branch_name': 'Office',
                    'fiscal_year': 'Year',
                    'order_probability': 'Probability',
                    'revenue': 'Sales',
                    'expenses': 'Cost'
                }
                
                print(f"Custom mapping: {custom_mapping}")
                
                # Test preview with custom mapping
                preview_result = import_service.get_preview_data(temp_csv_path, 'csv', custom_mapping)
                
                assert preview_result['success'], f"Preview with custom mapping failed: {preview_result.get('error', 'Unknown error')}"
                print(f"✓ Preview with custom mapping successful: {len(preview_result['data'])} rows")
                for i, row in enumerate(preview_result['data']):
                    print(f"  Row {i+1}: {row.get('project_code', 'N/A')} - {row.get('project_name', 'N/A')}")
                
                # Test import execution with custom mapping
                print("\n--- Import Execution with Custom Mapping Test ---")
                
                # Check initial project count
                initial_count = Project.query.count()
                print(f"Initial project count: {initial_count}")
                
                # Execute import with custom mapping
                import_result = import_service.execute_import(temp_csv_path, 'csv', custom_mapping)
                
                assert import_result['success'], f"Import execution with custom mapping failed: {import_result.get('error', 'Unknown error')}"
                print(f"✓ Import with custom mapping executed successfully")
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
                    Project.project_code.like('PROJ-MAP-%')
                ).all()
                
                print("\nImported projects with custom mapping:")
                for project in imported_projects:
                    print(f"  - {project.project_code}: {project.project_name}")
                    print(f"    Branch: {project.branch.branch_name if project.branch else 'N/A'}")
                    print(f"    Revenue: {project.revenue}, Expenses: {project.expenses}")
                    print(f"    Gross Profit: {project.gross_profit}")
                
            # Test branch creation with custom mapping
            print("\n--- Branch Creation with Custom Mapping Test ---")
            mapping_branch = Branch.query.filter_by(branch_name='マッピング支社').first()
            assert mapping_branch is not None, "Branch was not created"
            print(f"✓ Branch created successfully: {mapping_branch.branch_code} - {mapping_branch.branch_name}")
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
        
        print("\n=== All column mapping tests passed! ===")

if __name__ == '__main__':
    success = test_csv_import_with_mapping()
    sys.exit(0 if success else 1)