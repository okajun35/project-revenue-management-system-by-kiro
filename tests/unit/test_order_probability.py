#!/usr/bin/env python3
"""
受注角度の記号表示テスト
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Project
from app.enums import OrderProbability


def test_order_probability_symbols():
    """受注角度の記号表示テスト"""
    print("=== 受注角度の記号表示テスト ===")
    
    app = create_app()
    with app.app_context():
        # データベース初期化
        db.create_all()
        
        # 既存データをクリア
        Project.query.delete()
        db.session.commit()
        
        # 各受注角度のテストデータを作成
        test_cases = [
            {
                'code': 'HIGH-2024-001',
                'name': '受注確実プロジェクト',
                'probability': 100,
                'expected_symbol': '〇',
                'expected_desc': '高'
            },
            {
                'code': 'MEDIUM-2024-001',
                'name': '受注可能性ありプロジェクト',
                'probability': 50,
                'expected_symbol': '△',
                'expected_desc': '中'
            },
            {
                'code': 'LOW-2024-001',
                'name': '受注困難プロジェクト',
                'probability': 0,
                'expected_symbol': '×',
                'expected_desc': '低'
            }
        ]
        
        print("\n1. プロジェクト作成と記号表示テスト")
        created_projects = []
        
        for i, case in enumerate(test_cases, 1):
            try:
                project = Project.create_with_validation(
                    project_code=case['code'],
                    project_name=case['name'],
                    fiscal_year=2024,
                    order_probability=case['probability'],
                    revenue=1000000.00,
                    expenses=800000.00
                )
                
                # 記号表示の確認
                if (project.order_probability_symbol == case['expected_symbol'] and
                    project.order_probability_description == case['expected_desc']):
                    print(f"✓ テストケース{i}: {case['expected_symbol']} ({case['expected_desc']}) - PASS")
                    created_projects.append(project)
                else:
                    print(f"✗ テストケース{i}: 期待値 {case['expected_symbol']} ({case['expected_desc']}), "
                          f"実際 {project.order_probability_symbol} ({project.order_probability_description}) - FAIL")
                
            except Exception as e:
                print(f"✗ テストケース{i}: エラー - {str(e)}")
        
        print("\n2. to_dict()メソッドでの記号表示テスト")
        for i, project in enumerate(created_projects, 1):
            data = project.to_dict()
            expected_case = test_cases[i-1]
            
            if (data['order_probability_symbol'] == expected_case['expected_symbol'] and
                data['order_probability_description'] == expected_case['expected_desc'] and
                data['order_probability'] == expected_case['probability']):
                print(f"✓ to_dict()テスト{i}: {data['order_probability_symbol']} ({data['order_probability_description']}) - PASS")
            else:
                print(f"✗ to_dict()テスト{i}: データが正しくありません - FAIL")
                print(f"  データ: {data['order_probability_symbol']} ({data['order_probability_description']})")
        
        print("\n3. Enumクラスの動作テスト")
        
        # from_value テスト
        try:
            high_enum = OrderProbability.from_value(100)
            medium_enum = OrderProbability.from_value(50)
            low_enum = OrderProbability.from_value(0)
            
            if (high_enum.symbol == '〇' and medium_enum.symbol == '△' and low_enum.symbol == '×'):
                print("✓ from_value()メソッド: PASS")
            else:
                print("✗ from_value()メソッド: FAIL")
        except Exception as e:
            print(f"✗ from_value()メソッド: エラー - {str(e)}")
        
        # from_symbol テスト
        try:
            high_enum = OrderProbability.from_symbol('〇')
            medium_enum = OrderProbability.from_symbol('△')
            low_enum = OrderProbability.from_symbol('×')
            
            if (high_enum.numeric_value == 100 and medium_enum.numeric_value == 50 and low_enum.numeric_value == 0):
                print("✓ from_symbol()メソッド: PASS")
            else:
                print("✗ from_symbol()メソッド: FAIL")
        except Exception as e:
            print(f"✗ from_symbol()メソッド: エラー - {str(e)}")
        
        # get_choices テスト
        try:
            choices = OrderProbability.get_choices()
            expected_choices = [(100, '〇 (高)'), (50, '△ (中)'), (0, '× (低)')]
            
            if choices == expected_choices:
                print("✓ get_choices()メソッド: PASS")
                print(f"  選択肢: {choices}")
            else:
                print("✗ get_choices()メソッド: FAIL")
                print(f"  期待値: {expected_choices}")
                print(f"  実際: {choices}")
        except Exception as e:
            print(f"✗ get_choices()メソッド: エラー - {str(e)}")
        
        print("\n=== テスト完了 ===")


if __name__ == '__main__':
    test_order_probability_symbols()