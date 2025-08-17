#!/usr/bin/env python3
"""
テンプレート構文チェッカーのデモンストレーション

このスクリプトは、TemplateCheckerクラスの機能を実際のテンプレートファイルで
デモンストレーションします。
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from tests.frontend.utils.template_checker import TemplateChecker


def main():
    """メイン実行関数"""
    print("=" * 60)
    print("テンプレート構文チェッカー デモンストレーション")
    print("=" * 60)
    
    # TemplateCheckerインスタンスを作成
    checker = TemplateChecker('app/templates')
    
    print("\n1. 構文チェック実行中...")
    syntax_errors = checker.check_syntax()
    
    print(f"   構文エラー数: {len(syntax_errors)}")
    if syntax_errors:
        for error in syntax_errors:
            print(f"   ❌ {error.template_path}:{error.line_number} - {error.message}")
            if error.suggestion:
                print(f"      💡 提案: {error.suggestion}")
    else:
        print("   ✅ 構文エラーは検出されませんでした")
    
    print("\n2. ブロック継承チェック実行中...")
    inheritance_errors = checker.check_block_inheritance()
    
    print(f"   継承エラー数: {len(inheritance_errors)}")
    if inheritance_errors:
        for error in inheritance_errors:
            print(f"   ❌ {error.template_path} -> {error.parent_template}")
            print(f"      {error.message}")
            if error.extra_blocks:
                print(f"      不正なブロック: {', '.join(error.extra_blocks)}")
    else:
        print("   ✅ ブロック継承エラーは検出されませんでした")
    
    print("\n3. 必須ブロックチェック実行中...")
    required_errors = checker.check_required_blocks()
    
    print(f"   必須ブロックエラー数: {len(required_errors)}")
    if required_errors:
        for error in required_errors:
            print(f"   ❌ {error.template_path}")
            print(f"      不足ブロック: {', '.join(error.missing_blocks)}")
    else:
        print("   ✅ 必須ブロックエラーは検出されませんでした")
    
    print("\n4. 主要テンプレートのレンダリングテスト実行中...")
    
    templates_to_test = [
        'dashboard.html',
        'projects/index.html',
        'projects/form.html',
        'projects/show.html',
        'branches/index.html',
        'branches/form.html',
        'branches/show.html'
    ]
    
    render_results = {}
    
    for template in templates_to_test:
        try:
            result = checker.render_test(template)
            render_results[template] = result
            
            status = "✅" if result.success else "❌"
            print(f"   {status} {template}")
            
            if result.success:
                print(f"      ブロック: {', '.join(result.blocks_found) if result.blocks_found else 'なし'}")
                print(f"      HTML長: {len(result.rendered_html)} 文字")
                
                # 重要な要素の存在確認
                if 'projects/index.html' == template:
                    has_datatable = 'DataTable(' in result.rendered_html
                    has_table_id = 'id="projects-table"' in result.rendered_html
                    print(f"      DataTable初期化: {'✅' if has_datatable else '❌'}")
                    print(f"      テーブルID: {'✅' if has_table_id else '❌'}")
                    
            else:
                print(f"      エラー: {result.error}")
                
        except Exception as e:
            print(f"   ❌ {template} - 例外: {str(e)}")
    
    print("\n5. 総合分析結果")
    print("-" * 40)
    
    total_errors = len(syntax_errors) + len(inheritance_errors) + len(required_errors)
    successful_renders = sum(1 for r in render_results.values() if r.success)
    total_renders = len(render_results)
    
    print(f"総エラー数: {total_errors}")
    print(f"レンダリング成功率: {successful_renders}/{total_renders} ({successful_renders/total_renders*100:.1f}%)")
    
    if total_errors == 0 and successful_renders == total_renders:
        print("\n🎉 すべてのテンプレートが正常です！")
    elif total_errors > 0:
        print(f"\n⚠️  {total_errors}個の問題が検出されました。修正をお勧めします。")
    else:
        print(f"\n✅ 構文は正常ですが、{total_renders - successful_renders}個のテンプレートでレンダリング問題があります。")
    
    print("\n" + "=" * 60)
    print("デモンストレーション完了")
    print("=" * 60)


if __name__ == '__main__':
    main()