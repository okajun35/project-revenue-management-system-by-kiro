"""
テンプレート構文チェッカーのテスト

TemplateCheckerクラスの機能をテストする
"""

import pytest
import tempfile
import os
from pathlib import Path
from tests.frontend.utils.template_checker import (
    TemplateChecker, 
    TemplateError, 
    InheritanceError, 
    MissingBlockError,
    RenderResult
)


class TestTemplateChecker:
    """TemplateCheckerクラスのテストクラス"""
    
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
    
    def test_check_syntax_valid_template(self):
        """正常なテンプレートの構文チェックテスト"""
        # 正常なテンプレートを作成
        valid_template = """{% extends "base.html" %}

{% block title %}Test Page{% endblock %}

{% block content %}
<p>This is a test page.</p>
{% endblock %}"""
        
        self.create_test_template('test_valid.html', valid_template)
        
        # 構文チェック実行
        errors = self.checker.check_syntax()
        
        # エラーがないことを確認
        assert len(errors) == 0
    
    def test_check_syntax_invalid_template(self):
        """構文エラーのあるテンプレートのチェックテスト"""
        # 構文エラーのあるテンプレート（不正なJinja2構文）
        invalid_template = """{% extends "base.html" %}

{% block title %}Test Page{% endblock %}

{% block content %}
<p>This has invalid syntax: {% invalid_tag_name %}</p>
{% endblock %}"""
        
        self.create_test_template('test_invalid.html', invalid_template)
        
        # 構文チェック実行
        errors = self.checker.check_syntax()
        
        # エラーが検出されることを確認
        assert len(errors) > 0
        assert any(error.error_type == "SyntaxError" for error in errors)
        assert any("test_invalid.html" in error.template_path for error in errors)
    
    def test_check_block_inheritance_valid(self):
        """正常なブロック継承のチェックテスト"""
        # 正常な継承テンプレートを作成
        valid_child = """{% extends "base.html" %}

{% block title %}Child Page{% endblock %}
{% block content %}
<p>Child content</p>
{% endblock %}
{% block scripts %}
<script>console.log('child script');</script>
{% endblock %}"""
        
        self.create_test_template('test_child.html', valid_child)
        
        # 継承チェック実行
        errors = self.checker.check_block_inheritance()
        
        # エラーがないことを確認
        inheritance_errors = [e for e in errors if e.template_path.endswith('test_child.html')]
        assert len(inheritance_errors) == 0
    
    def test_check_block_inheritance_extra_blocks(self):
        """親テンプレートに存在しないブロックがある場合のテスト"""
        # 親テンプレートに存在しないブロックを含むテンプレート
        child_with_extra = """{% extends "base.html" %}

{% block title %}Child Page{% endblock %}
{% block content %}
<p>Child content</p>
{% endblock %}
{% block nonexistent_block %}
<p>This block doesn't exist in parent</p>
{% endblock %}"""
        
        self.create_test_template('test_extra_blocks.html', child_with_extra)
        
        # 継承チェック実行
        errors = self.checker.check_block_inheritance()
        
        # エラーが検出されることを確認
        extra_block_errors = [e for e in errors 
                             if e.template_path.endswith('test_extra_blocks.html') 
                             and e.error_type == "ExtraBlocks"]
        assert len(extra_block_errors) > 0
        assert 'nonexistent_block' in extra_block_errors[0].extra_blocks
    
    def test_check_required_blocks_missing(self):
        """必須ブロックが不足している場合のテスト"""
        # titleブロックが不足しているテンプレート
        missing_required = """{% extends "base.html" %}

{% block content %}
<p>Content without title block</p>
{% endblock %}"""
        
        self.create_test_template('test_missing_required.html', missing_required)
        
        # 必須ブロックチェック実行
        errors = self.checker.check_required_blocks()
        
        # titleブロックが不足していることを確認
        missing_errors = [e for e in errors 
                         if e.template_path.endswith('test_missing_required.html')]
        assert len(missing_errors) > 0
        assert 'title' in missing_errors[0].missing_blocks
    
    def test_check_required_blocks_complete(self):
        """必須ブロックが全て揃っている場合のテスト"""
        # 必須ブロックが全て含まれているテンプレート
        complete_template = """{% extends "base.html" %}

{% block title %}Complete Page{% endblock %}
{% block content %}
<p>Complete content</p>
{% endblock %}"""
        
        self.create_test_template('test_complete.html', complete_template)
        
        # 必須ブロックチェック実行
        errors = self.checker.check_required_blocks()
        
        # エラーがないことを確認
        complete_errors = [e for e in errors 
                          if e.template_path.endswith('test_complete.html')]
        assert len(complete_errors) == 0
    
    def test_render_test_success(self):
        """正常なテンプレートのレンダリングテスト"""
        # レンダリング可能なテンプレートを作成
        renderable_template = """{% extends "base.html" %}

{% block title %}Renderable Page{% endblock %}
{% block content %}
<p>This can be rendered: {{ test_var }}</p>
{% endblock %}"""
        
        self.create_test_template('test_renderable.html', renderable_template)
        
        # レンダリングテスト実行
        result = self.checker.render_test('test_renderable.html', {'test_var': 'Hello World'})
        
        # レンダリング成功を確認
        assert result.success is True
        assert result.rendered_html is not None
        assert 'Hello World' in result.rendered_html
        assert 'Renderable Page' in result.rendered_html
    
    def test_render_test_failure(self):
        """レンダリングエラーのテスト"""
        # 存在しないテンプレートのレンダリングテスト
        result = self.checker.render_test('nonexistent_template.html')
        
        # レンダリング失敗を確認
        assert result.success is False
        assert result.error is not None
        assert 'テンプレートが見つかりません' in result.error
    
    def test_get_template_blocks(self):
        """テンプレートからブロック名を抽出するテスト"""
        # ブロックを含むテンプレートを作成
        template_with_blocks = """{% extends "base.html" %}

{% block title %}Test Title{% endblock %}
{% block extra_css %}
<style>body { color: red; }</style>
{% endblock %}
{% block content %}
<p>Test content</p>
{% endblock %}
{% block scripts %}
<script>console.log('test');</script>
{% endblock %}"""
        
        self.create_test_template('test_blocks.html', template_with_blocks)
        
        # ブロック抽出実行
        blocks = self.checker._get_template_blocks(Path('test_blocks.html'))
        
        # 期待されるブロックが抽出されることを確認
        expected_blocks = ['title', 'extra_css', 'content', 'scripts']
        assert set(blocks) == set(expected_blocks)
    
    def test_analyze_template_inheritance(self):
        """テンプレート継承関係の解析テスト"""
        # 継承関係のあるテンプレートを作成
        child_template = """{% extends "base.html" %}

{% block title %}Child Title{% endblock %}
{% block content %}Child content{% endblock %}"""
        
        self.create_test_template('test_inheritance.html', child_template)
        
        # 継承関係解析実行
        inheritance_info = self.checker._analyze_template_inheritance(Path('test_inheritance.html'))
        
        # 継承関係が正しく解析されることを確認
        assert inheritance_info['parent_template'] == 'base.html'
        assert 'title' in inheritance_info['blocks']
        assert 'content' in inheritance_info['blocks']
    
    def test_projects_index_template_real(self):
        """実際のプロジェクト一覧テンプレートのテスト"""
        # 実際のテンプレートディレクトリを使用
        real_checker = TemplateChecker('app/templates')
        
        # 構文チェック
        syntax_errors = real_checker.check_syntax()
        
        # 継承チェック
        inheritance_errors = real_checker.check_block_inheritance()
        
        # 必須ブロックチェック
        required_block_errors = real_checker.check_required_blocks()
        
        # プロジェクト一覧テンプレートのレンダリングテスト
        render_result = real_checker.render_test('projects/index.html')
        
        # 結果を出力（デバッグ用）
        print(f"構文エラー数: {len(syntax_errors)}")
        print(f"継承エラー数: {len(inheritance_errors)}")
        print(f"必須ブロックエラー数: {len(required_block_errors)}")
        print(f"レンダリング成功: {render_result.success}")
        
        if syntax_errors:
            print("構文エラー:")
            for error in syntax_errors:
                print(f"  - {error.template_path}: {error.message}")
        
        if inheritance_errors:
            print("継承エラー:")
            for error in inheritance_errors:
                print(f"  - {error.template_path}: {error.message}")
        
        if required_block_errors:
            print("必須ブロックエラー:")
            for error in required_block_errors:
                print(f"  - {error.template_path}: {error.message}")
        
        if not render_result.success:
            print(f"レンダリングエラー: {render_result.error}")
        
        # 基本的な検証（エラーがあっても失敗させない - 情報収集目的）
        assert isinstance(syntax_errors, list)
        assert isinstance(inheritance_errors, list)
        assert isinstance(required_block_errors, list)
        assert isinstance(render_result, RenderResult)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])