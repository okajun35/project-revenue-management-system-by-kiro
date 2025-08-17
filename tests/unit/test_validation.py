#!/usr/bin/env python3
"""
プロジェクトデータモデルとバリデーションのテスト（クリーン版）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Project, Branch, ValidationError
from app.forms import ProjectForm
from app.services.project_service import ProjectService
from app.services.validation_service import ValidationService


def test_project_model_validation(app_context, sample_branch):
    """Projectモデルの検証テスト"""
    print("=== Projectモデル検証テスト ===")
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # 正常なプロジェクトデータ
    valid_data = {
        'project_code': f'TEST-2024-{unique_id}',
        'project_name': f'テストプロジェクト{unique_id}',
        'branch_id': sample_branch.id,
        'fiscal_year': 2024,
        'order_probability': 100,  # 有効な値に修正
        'revenue': 1000000.00,
        'expenses': 800000.00
    }
    
    # 正常ケースのテスト
    try:
        project = Project.create_with_validation(**valid_data)
        print("✓ 正常データの検証: PASS")
        assert project.project_code == f'TEST-2024-{unique_id}'
        assert project.gross_profit == 200000.00  # 1000000 - 800000
    except Exception as e:
        print(f"✗ 正常データの検証: ERROR - {str(e)}")
        assert False, f"正常データでエラーが発生: {str(e)}"


def test_wtforms_validation(app_context, sample_branch):
    """WTFormsの検証テスト"""
    print("\n=== WTForms検証テスト ===")
    
    with app_context.test_request_context():
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # 正常なフォームデータ
        valid_form_data = {
            'project_code': f'FORM-2024-{unique_id}',
            'project_name': f'フォームテストプロジェクト{unique_id}',
            'branch_id': sample_branch.id,
            'fiscal_year': 2024,
            'order_probability': 100,
            'revenue': 1500000.00,
            'expenses': 1200000.00,
            'csrf_token': 'test_token'
        }
        
        # 正常ケースのテスト
        form = ProjectForm(data=valid_form_data)
        # 支社の選択肢を設定
        form.branch_id.choices = [(sample_branch.id, sample_branch.branch_name)]
        # 年度の選択肢を設定
        from app.models import FiscalYear
        test_fiscal_year = FiscalYear.query.filter_by(year=2024).first()
        if not test_fiscal_year:
            test_fiscal_year = FiscalYear.create_with_validation(year=2024, year_name='2024年度')
        form.fiscal_year.choices = [(test_fiscal_year.year, test_fiscal_year.year_name)]
        
        if form.validate():
            print("✓ 正常フォームデータの検証: PASS")
            assert True
        else:
            print(f"✗ 正常フォームデータの検証: FAIL - {form.errors}")
            assert False, f"正常フォームデータでバリデーションエラー: {form.errors}"
        
        # 異常ケースのテスト
        invalid_cases = [
            # プロジェクトコードに無効文字
            {
                'data': {**valid_form_data, 'project_code': 'INVALID@CODE'},
                'field': 'project_code'
            },
            # プロジェクト名が長すぎる
            {
                'data': {**valid_form_data, 'project_name': 'A' * 201},
                'field': 'project_name'
            },
            # 年度が範囲外
            {
                'data': {**valid_form_data, 'fiscal_year': 3000},
                'field': 'fiscal_year'
            }
        ]
        
        for i, test_case in enumerate(invalid_cases, 1):
            form = ProjectForm(data=test_case['data'])
            # 支社の選択肢を設定
            form.branch_id.choices = [(sample_branch.id, sample_branch.branch_name)]
            # 年度の選択肢を設定
            form.fiscal_year.choices = [(test_fiscal_year.year, test_fiscal_year.year_name)]
            if not form.validate() and test_case['field'] in form.errors:
                print(f"✓ フォーム異常ケース{i}: PASS")
            else:
                print(f"✗ フォーム異常ケース{i}: FAIL - {form.errors}")
                assert False, f"異常ケース{i}でバリデーションが期待通りに動作しない"
        
        print("WTForms検証テスト完了\n")


def test_validation_service(app_context, sample_branch):
    """ValidationServiceのテスト"""
    print("\n=== ValidationService テスト ===")
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # 正常なデータ
    valid_data = {
        'project_code': f'VALID-2024-{unique_id}',
        'project_name': f'バリデーションテストプロジェクト{unique_id}',
        'branch_id': sample_branch.id,
        'fiscal_year': 2024,
        'order_probability': 50,
        'revenue': 2000000.00,
        'expenses': 1500000.00
    }
    
    # ValidationServiceのテスト
    errors = ValidationService.validate_project_data(valid_data)
    if not errors:
        print("✓ ValidationService正常データ: PASS")
        assert True
    else:
        print(f"✗ ValidationService正常データ: FAIL - {[e.message for e in errors]}")
        assert False, f"正常データでバリデーションエラー: {[e.message for e in errors]}"
    
    print("ValidationService テスト完了\n")


def test_gross_profit_calculation(app_context, sample_branch):
    """粗利計算のテスト"""
    print("\n=== 粗利計算テスト ===")
    
    test_cases = [
        # (売上, 経費, 期待粗利)
        (1000000, 800000, 200000),
        (2000000, 1500000, 500000),
        (500000, 600000, -100000),  # 赤字ケース
        (0, 0, 0),  # ゼロケース
    ]
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    for i, (revenue, expenses, expected_profit) in enumerate(test_cases, 1):
        project_data = {
            'project_code': f'PROFIT-TEST-{unique_id}-{i:03d}',
            'project_name': f'粗利テストプロジェクト{unique_id}-{i}',
            'branch_id': sample_branch.id,
            'fiscal_year': 2024,
            'order_probability': 100,
            'revenue': revenue,
            'expenses': expenses
        }
        
        project = Project.create_with_validation(**project_data)
        
        if project.gross_profit == expected_profit:
            print(f"✓ 粗利計算ケース{i}: PASS (売上:{revenue}, 経費:{expenses}, 粗利:{project.gross_profit})")
            assert project.gross_profit == expected_profit
        else:
            print(f"✗ 粗利計算ケース{i}: FAIL (期待:{expected_profit}, 実際:{project.gross_profit})")
            assert False, f"粗利計算が間違っています: 期待{expected_profit}, 実際{project.gross_profit}"
    
    print("粗利計算テスト完了\n")