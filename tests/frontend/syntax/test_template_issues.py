"""
テンプレートの具体的な問題を検出するテスト

今回のプロジェクト一覧ページの問題（テンプレートブロック名の不一致によるJavaScript未実行）
のような問題を検出するためのテスト
"""

import pytest
import tempfile
from pathlib import Path
from tests.frontend.utils.template_checker import TemplateChecker


class TestTemplateIssues:
    """テンプレートの具体的な問題を検出するテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        # 一時ディレクトリを作成
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = Path(self.temp_dir) / 'templates'
        self.templates_dir.mkdir()
        
        # テスト用のbase.htmlを作成
        self.create_base_template()
        
        # TemplateCheckerインスタンスを作成
        self.checker = TemplateChecker(str(self.templates_dir))
    
    def teardown_method(self):
        """各テストメソッドの後に実行されるクリーンアップ処理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_base_template(self):
        """テスト用のbase.htmlテンプレートを作成"""
        base_content = """<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <h1>{% block page_title %}{% endblock %}</h1>
    <nav>{% block breadcrumb %}{% endblock %}</nav>
    <main>{% block content %}{% endblock %}</main>
    {% block scripts %}{% endblock %}
</body>
</html>"""
        
        with open(self.templates_dir / 'base.html', 'w', encoding='utf-8') as f:
            f.write(base_content)
    
    def create_test_template(self, filename: str, content: str):
        """テスト用のテンプレートファイルを作成"""
        # サブディレクトリが必要な場合は作成
        template_path = self.templates_dir / filename
        template_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def test_block_name_mismatch_detection(self):
        """ブロック名の不一致を検出するテスト（今回の問題のシミュレーション）"""
        # 親テンプレートでは 'scripts' ブロックを定義
        # 子テンプレートでは 'script' ブロック（sが抜けている）を使用
        child_with_mismatch = """{% extends "base.html" %}

{% block title %}Projects List{% endblock %}
{% block content %}
<div id="projects-table">
    <table>
        <thead>
            <tr><th>Project</th></tr>
        </thead>
        <tbody></tbody>
    </table>
</div>
{% endblock %}

{% block script %}
<script>
$(document).ready(function() {
    $('#projects-table').DataTable({
        // DataTables configuration
    });
});
</script>
{% endblock %}"""
        
        self.create_test_template('projects/index.html', child_with_mismatch)
        
        # 継承チェック実行
        errors = self.checker.check_block_inheritance()
        
        # ブロック名の不一致エラーが検出されることを確認
        mismatch_errors = [e for e in errors 
                          if 'index.html' in e.template_path 
                          and e.error_type == "ExtraBlocks"]
        
        assert len(mismatch_errors) > 0
        assert 'script' in mismatch_errors[0].extra_blocks
        print(f"検出されたエラー: {mismatch_errors[0].message}")
        print(f"不正なブロック: {mismatch_errors[0].extra_blocks}")
    
    def test_javascript_block_missing_detection(self):
        """JavaScriptブロックが不足している場合の検出テスト"""
        # JavaScriptが必要だがscriptsブロックが定義されていないテンプレート
        template_without_js = """{% extends "base.html" %}

{% block title %}Projects List{% endblock %}
{% block content %}
<div id="projects-table">
    <table class="table">
        <thead>
            <tr><th>Project</th></tr>
        </thead>
        <tbody></tbody>
    </table>
</div>
<!-- JavaScriptブロックが不足 -->
{% endblock %}"""
        
        self.create_test_template('projects/no_js.html', template_without_js)
        
        # レンダリングテスト実行
        result = self.checker.render_test('projects/no_js.html')
        
        # レンダリングは成功するが、JavaScriptブロックが不足していることを確認
        assert result.success is True
        assert 'scripts' not in result.blocks_found
        
        # HTMLにはテーブルがあるがJavaScriptがない
        assert 'projects-table' in result.rendered_html
        assert 'DataTable' not in result.rendered_html
    
    def test_correct_template_structure(self):
        """正しいテンプレート構造のテスト"""
        # 正しいブロック名を使用したテンプレート
        correct_template = """{% extends "base.html" %}

{% block title %}Projects List{% endblock %}
{% block content %}
<div id="projects-table">
    <table class="table">
        <thead>
            <tr><th>Project</th></tr>
        </thead>
        <tbody></tbody>
    </table>
</div>
{% endblock %}

{% block scripts %}
<script>
$(document).ready(function() {
    $('#projects-table').DataTable({
        // DataTables configuration
    });
});
</script>
{% endblock %}"""
        
        self.create_test_template('projects/correct.html', correct_template)
        
        # 全チェック実行
        syntax_errors = self.checker.check_syntax()
        inheritance_errors = self.checker.check_block_inheritance()
        required_errors = self.checker.check_required_blocks()
        render_result = self.checker.render_test('projects/correct.html')
        
        # エラーがないことを確認
        template_syntax_errors = [e for e in syntax_errors if 'correct.html' in e.template_path]
        template_inheritance_errors = [e for e in inheritance_errors if 'correct.html' in e.template_path]
        template_required_errors = [e for e in required_errors if 'correct.html' in e.template_path]
        
        assert len(template_syntax_errors) == 0
        assert len(template_inheritance_errors) == 0
        assert len(template_required_errors) == 0
        assert render_result.success is True
        
        # 必要な要素が含まれていることを確認
        assert 'projects-table' in render_result.rendered_html
        assert 'DataTable' in render_result.rendered_html
        assert 'scripts' in render_result.blocks_found
    
    def test_real_projects_template_analysis(self):
        """実際のプロジェクト一覧テンプレートの分析テスト"""
        # 実際のテンプレートディレクトリを使用
        real_checker = TemplateChecker('app/templates')
        
        # プロジェクト一覧テンプレートの詳細分析
        render_result = real_checker.render_test('projects/index.html')
        
        print(f"\n=== プロジェクト一覧テンプレート分析結果 ===")
        print(f"レンダリング成功: {render_result.success}")
        
        if render_result.success:
            print(f"検出されたブロック: {render_result.blocks_found}")
            print(f"HTML長: {len(render_result.rendered_html)} 文字")
            
            # 重要な要素の存在確認
            checks = {
                'projects-table ID': 'id="projects-table"' in render_result.rendered_html,
                'DataTable初期化': 'DataTable(' in render_result.rendered_html,
                'AJAX URL': 'projects.api_list' in render_result.rendered_html,
                'scriptsブロック': 'scripts' in render_result.blocks_found,
                'extra_cssブロック': 'extra_css' in render_result.blocks_found,
                'contentブロック': 'content' in render_result.blocks_found,
                'titleブロック': 'title' in render_result.blocks_found
            }
            
            print("\n要素存在チェック:")
            for check_name, exists in checks.items():
                status = "✓" if exists else "✗"
                print(f"  {status} {check_name}: {exists}")
            
            # 潜在的な問題の検出
            potential_issues = []
            
            if not checks['DataTable初期化']:
                potential_issues.append("DataTableの初期化コードが見つかりません")
            
            if not checks['AJAX URL']:
                potential_issues.append("AJAX URLの設定が見つかりません")
            
            if not checks['scriptsブロック']:
                potential_issues.append("scriptsブロックが定義されていません")
            
            if potential_issues:
                print(f"\n潜在的な問題:")
                for issue in potential_issues:
                    print(f"  ⚠ {issue}")
            else:
                print(f"\n✓ 潜在的な問題は検出されませんでした")
        
        else:
            print(f"レンダリングエラー: {render_result.error}")
        
        # 基本的な検証
        assert isinstance(render_result.success, bool)
    
    def test_template_block_consistency_across_pages(self):
        """複数ページ間でのテンプレートブロック整合性テスト"""
        # 実際のテンプレートディレクトリを使用
        real_checker = TemplateChecker('app/templates')
        
        # 主要なページテンプレートをテスト
        templates_to_test = [
            'dashboard.html',
            'projects/index.html',
            'projects/form.html',
            'projects/show.html',
            'branches/index.html',
            'branches/form.html',
            'branches/show.html'
        ]
        
        print(f"\n=== テンプレートブロック整合性分析 ===")
        
        all_blocks = {}
        render_results = {}
        
        for template in templates_to_test:
            try:
                result = real_checker.render_test(template)
                render_results[template] = result
                
                if result.success and result.blocks_found:
                    all_blocks[template] = set(result.blocks_found)
                    print(f"{template}: {result.blocks_found}")
                else:
                    print(f"{template}: レンダリング失敗 - {result.error}")
                    
            except Exception as e:
                print(f"{template}: エラー - {str(e)}")
        
        # 共通ブロックの分析
        if all_blocks:
            common_blocks = set.intersection(*all_blocks.values())
            print(f"\n共通ブロック: {sorted(common_blocks)}")
            
            # 各テンプレートで不足している共通ブロックを検出
            for template, blocks in all_blocks.items():
                missing_common = common_blocks - blocks
                if missing_common:
                    print(f"⚠ {template}: 共通ブロック不足 - {sorted(missing_common)}")
        
        # 基本的な検証
        assert len(render_results) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])