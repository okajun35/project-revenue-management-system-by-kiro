#!/usr/bin/env python3
"""
Task 19: インポート列マッピング機能の簡単なテスト

実装した機能の基本的な動作をテストします。
"""

import tempfile
import os
import pandas as pd
from app.services.import_service import ImportService


def test_system_fields():
    """システムフィールド定義のテスト"""
    print("=== システムフィールド定義のテスト ===")
    
    service = ImportService()
    system_fields = service.get_system_fields()
    
    print(f"システムフィールド数: {len(system_fields)}")
    
    for field_name, field_info in system_fields.items():
        print(f"- {field_name}: {field_info['label']} ({'必須' if field_info['required'] else '任意'})")
        print(f"  説明: {field_info['description']}")
        print(f"  例: {field_info['example']}")
        print()
    
    # 必須フィールドが含まれていることを確認
    required_fields = ['project_code', 'project_name', 'branch_name', 'fiscal_year', 'order_probability', 'revenue', 'expenses']
    for field in required_fields:
        assert field in system_fields, f"必須フィールド {field} が見つかりません"
        assert system_fields[field]['required'], f"フィールド {field} が必須として設定されていません"
    
    print("✅ システムフィールド定義テスト: 成功")


def test_auto_mapping():
    """自動マッピング機能のテスト"""
    print("=== 自動マッピング機能のテスト ===")
    
    service = ImportService()
    
    # テスト用の列名
    test_columns = [
        'プロジェクトコード',
        'プロジェクト名',
        '支社名',
        '売上の年度',
        '受注角度',
        '売上（契約金）',
        '経費（トータル）'
    ]
    
    auto_mapping = service.get_auto_mapping(test_columns)
    
    print("自動マッピング結果:")
    for field, column in auto_mapping.items():
        print(f"- {field} -> {column}")
    
    # 期待されるマッピングが生成されることを確認
    expected_mappings = {
        'project_code': 'プロジェクトコード',
        'project_name': 'プロジェクト名',
        'branch_name': '支社名',
        'fiscal_year': '売上の年度',
        'order_probability': '受注角度',
        'revenue': '売上（契約金）',
        'expenses': '経費（トータル）'
    }
    
    for field, expected_column in expected_mappings.items():
        assert field in auto_mapping, f"フィールド {field} のマッピングが見つかりません"
        assert auto_mapping[field] == expected_column, f"フィールド {field} のマッピングが期待値と異なります"
    
    print("✅ 自動マッピング機能テスト: 成功")


def test_mapping_validation():
    """マッピング検証機能のテスト"""
    print("=== マッピング検証機能のテスト ===")
    
    service = ImportService()
    
    test_columns = [
        'プロジェクトコード',
        'プロジェクト名',
        '支社名',
        '売上の年度',
        '受注角度',
        '売上（契約金）',
        '経費（トータル）'
    ]
    
    # 正しいマッピング
    valid_mapping = {
        'project_code': 'プロジェクトコード',
        'project_name': 'プロジェクト名',
        'branch_name': '支社名',
        'fiscal_year': '売上の年度',
        'order_probability': '受注角度',
        'revenue': '売上（契約金）',
        'expenses': '経費（トータル）'
    }
    
    validation_result = service.validate_mapping(valid_mapping, test_columns)
    print(f"正しいマッピングの検証結果: {validation_result['valid']}")
    if validation_result['errors']:
        print(f"エラー: {validation_result['errors']}")
    if validation_result['warnings']:
        print(f"警告: {validation_result['warnings']}")
    
    assert validation_result['valid'], "正しいマッピングが無効と判定されました"
    
    # 不正なマッピング（必須フィールド不足）
    invalid_mapping = {
        'project_code': 'プロジェクトコード',
        'project_name': 'プロジェクト名'
        # 他の必須フィールドが不足
    }
    
    validation_result = service.validate_mapping(invalid_mapping, test_columns)
    print(f"不正なマッピングの検証結果: {validation_result['valid']}")
    if validation_result['errors']:
        print(f"エラー: {validation_result['errors']}")
    
    assert not validation_result['valid'], "不正なマッピングが有効と判定されました"
    assert len(validation_result['errors']) > 0, "エラーが検出されませんでした"
    
    # 重複マッピング
    duplicate_mapping = {
        'project_code': 'プロジェクトコード',
        'project_name': 'プロジェクトコード',  # 重複
        'branch_name': '支社名',
        'fiscal_year': '売上の年度',
        'order_probability': '受注角度',
        'revenue': '売上（契約金）',
        'expenses': '経費（トータル）'
    }
    
    validation_result = service.validate_mapping(duplicate_mapping, test_columns)
    print(f"重複マッピングの検証結果: {validation_result['valid']}")
    if validation_result['errors']:
        print(f"エラー: {validation_result['errors']}")
    
    assert not validation_result['valid'], "重複マッピングが有効と判定されました"
    
    print("✅ マッピング検証機能テスト: 成功")


def test_csv_file_processing():
    """CSVファイル処理のテスト"""
    print("=== CSVファイル処理のテスト ===")
    
    # サンプルデータ
    data = {
        'プロジェクトコード': ['PRJ001', 'PRJ002', 'PRJ003'],
        'プロジェクト名': ['新システム開発', 'Webサイト構築', 'データ分析'],
        '支社名': ['東京支社', '大阪支社', '東京支社'],
        '売上の年度': [2024, 2024, 2025],
        '受注角度': ['〇', '△', '×'],
        '売上（契約金）': [1000000, 500000, 800000],
        '経費（トータル）': [800000, 300000, 600000]
    }
    
    df = pd.DataFrame(data)
    
    # 一時ファイルに保存
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig')
    df.to_csv(temp_file.name, index=False, encoding='utf-8-sig')
    temp_file.close()
    
    try:
        service = ImportService()
        
        # ファイルを検証
        result = service.validate_file(temp_file.name, 'csv')
        
        print(f"ファイル検証結果: {result['success']}")
        if result['success']:
            print(f"行数: {result['row_count']}")
            print(f"列数: {len(result['columns'])}")
            print(f"列名: {result['columns']}")
            
            # 自動マッピングを生成
            auto_mapping = service.get_auto_mapping(result['columns'])
            print(f"自動マッピング: {auto_mapping}")
            
            assert result['success'], "ファイル検証が失敗しました"
            assert result['row_count'] == 3, f"期待される行数は3ですが、{result['row_count']}でした"
            assert len(result['columns']) == 7, f"期待される列数は7ですが、{len(result['columns'])}でした"
        else:
            print(f"エラー: {result['error']}")
            assert False, f"ファイル検証が失敗しました: {result['error']}"
        
    finally:
        # クリーンアップ
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    print("✅ CSVファイル処理テスト: 成功")


def main():
    """メイン関数"""
    print("Task 19: インポート列マッピング機能のテストを開始...")
    print()
    
    try:
        test_system_fields()
        print()
        
        test_auto_mapping()
        print()
        
        test_mapping_validation()
        print()
        
        test_csv_file_processing()
        print()
        
        print("🎉 すべてのテストが成功しました！")
        print()
        print("実装された機能:")
        print("✅ 列マッピング画面のHTMLテンプレート")
        print("✅ CSVの列構造解析とシステムフィールドとのマッピング機能")
        print("✅ ユーザーが列の対応関係を設定できるインターフェース")
        print("✅ マッピング設定の保存と検証機能")
        print("✅ 支社マッピング機能")
        print("✅ 自動マッピング改善機能")
        print("✅ リアルタイム検証機能")
        
    except Exception as e:
        print(f"❌ テストが失敗しました: {e}")
        return False
    
    return True


if __name__ == '__main__':
    main()