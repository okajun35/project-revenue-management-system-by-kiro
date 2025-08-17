"""
テンプレート構文チェッカー

Jinjaテンプレートの構文エラーを検出し、ブロック継承の整合性をチェックする
"""

import os
import re
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError, meta
from jinja2.exceptions import TemplateNotFound


@dataclass
class TemplateError:
    """テンプレートエラーの情報を格納するデータクラス"""
    template_path: str
    line_number: int
    error_type: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class InheritanceError:
    """ブロック継承エラーの情報を格納するデータクラス"""
    template_path: str
    parent_template: str
    error_type: str
    message: str
    missing_blocks: Optional[List[str]] = None
    extra_blocks: Optional[List[str]] = None


@dataclass
class MissingBlockError:
    """必須ブロック不足エラーの情報を格納するデータクラス"""
    template_path: str
    missing_blocks: List[str]
    message: str


@dataclass
class RenderResult:
    """テンプレートレンダリング結果を格納するデータクラス"""
    template_path: str
    success: bool
    rendered_html: Optional[str] = None
    error: Optional[str] = None
    blocks_found: Optional[List[str]] = None


class TemplateChecker:
    """Jinjaテンプレートの構文チェックとブロック継承の検証を行うクラス"""
    
    # 必須ブロックの定義
    REQUIRED_BLOCKS = {
        'title',      # ページタイトル
        'content',    # メインコンテンツ
    }
    
    # 推奨ブロックの定義
    RECOMMENDED_BLOCKS = {
        'scripts',    # JavaScript
        'extra_css', # 追加CSS
        'page_title', # ページヘッダータイトル
        'breadcrumb', # パンくずリスト
    }
    
    def __init__(self, templates_dir: str = 'app/templates'):
        """
        TemplateCheckerを初期化
        
        Args:
            templates_dir: テンプレートディレクトリのパス
        """
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
    def check_syntax(self) -> List[TemplateError]:
        """
        Jinjaテンプレートの構文チェックを実行
        
        Returns:
            構文エラーのリスト
        """
        errors = []
        
        for template_path in self._get_template_files():
            try:
                # テンプレートをパースして構文チェック
                with open(self.templates_dir / template_path, 'r', encoding='utf-8') as f:
                    template_source = f.read()
                
                # Jinja2環境でパース
                self.env.parse(template_source)
                
            except TemplateSyntaxError as e:
                errors.append(TemplateError(
                    template_path=str(template_path),
                    line_number=e.lineno or 0,
                    error_type="SyntaxError",
                    message=str(e),
                    suggestion=self._get_syntax_suggestion(str(e))
                ))
            except Exception as e:
                errors.append(TemplateError(
                    template_path=str(template_path),
                    line_number=0,
                    error_type="ParseError",
                    message=f"テンプレートの解析に失敗しました: {str(e)}",
                    suggestion="テンプレートファイルの文字エンコーディングを確認してください"
                ))
        
        return errors
    
    def check_block_inheritance(self) -> List[InheritanceError]:
        """
        ブロック継承の整合性をチェック
        
        Returns:
            継承エラーのリスト
        """
        errors = []
        
        for template_path in self._get_template_files():
            try:
                # テンプレートの継承関係を解析
                inheritance_info = self._analyze_template_inheritance(template_path)
                
                if inheritance_info['parent_template']:
                    # 親テンプレートのブロックを取得
                    parent_blocks = self._get_template_blocks(inheritance_info['parent_template'])
                    child_blocks = inheritance_info['blocks']
                    
                    # ブロック名の不一致をチェック
                    block_errors = self._check_block_consistency(
                        template_path, 
                        inheritance_info['parent_template'],
                        parent_blocks, 
                        child_blocks
                    )
                    errors.extend(block_errors)
                    
            except Exception as e:
                errors.append(InheritanceError(
                    template_path=str(template_path),
                    parent_template="",
                    error_type="InheritanceAnalysisError",
                    message=f"継承関係の解析に失敗しました: {str(e)}"
                ))
        
        return errors
    
    def check_required_blocks(self) -> List[MissingBlockError]:
        """
        必須ブロックの存在確認
        
        Returns:
            必須ブロック不足エラーのリスト
        """
        errors = []
        
        for template_path in self._get_template_files():
            # 除外するテンプレート
            if (template_path.name == 'base.html' or  # 親テンプレート
                'components' in str(template_path) or  # コンポーネントテンプレート
                template_path.name.startswith('_')):   # パーシャルテンプレート
                continue
                
            try:
                # extendsを使用しているテンプレートのみチェック
                inheritance_info = self._analyze_template_inheritance(template_path)
                if not inheritance_info['parent_template']:
                    continue  # 継承していないテンプレートはスキップ
                
                blocks = self._get_template_blocks(template_path)
                missing_blocks = self.REQUIRED_BLOCKS - set(blocks)
                
                if missing_blocks:
                    errors.append(MissingBlockError(
                        template_path=str(template_path),
                        missing_blocks=list(missing_blocks),
                        message=f"必須ブロックが不足しています: {', '.join(missing_blocks)}"
                    ))
                    
            except Exception as e:
                errors.append(MissingBlockError(
                    template_path=str(template_path),
                    missing_blocks=[],
                    message=f"ブロック解析に失敗しました: {str(e)}"
                ))
        
        return errors
    
    def render_test(self, template_path: str, context: Optional[Dict] = None) -> RenderResult:
        """
        テンプレートレンダリングテスト
        
        Args:
            template_path: テンプレートファイルのパス
            context: レンダリング用のコンテキスト
            
        Returns:
            レンダリング結果
        """
        if context is None:
            context = self._get_default_context()
        
        try:
            template = self.env.get_template(template_path)
            rendered_html = template.render(**context)
            blocks = self._get_template_blocks(Path(template_path))
            
            return RenderResult(
                template_path=template_path,
                success=True,
                rendered_html=rendered_html,
                blocks_found=blocks
            )
            
        except TemplateNotFound as e:
            return RenderResult(
                template_path=template_path,
                success=False,
                error=f"テンプレートが見つかりません: {str(e)}"
            )
        except Exception as e:
            return RenderResult(
                template_path=template_path,
                success=False,
                error=f"レンダリングエラー: {str(e)}"
            )
    
    def _get_template_files(self) -> List[Path]:
        """テンプレートファイルの一覧を取得"""
        template_files = []
        
        for root, dirs, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith('.html'):
                    full_path = Path(root) / file
                    relative_path = full_path.relative_to(self.templates_dir)
                    template_files.append(relative_path)
        
        return template_files
    
    def _get_template_blocks(self, template_path: Path) -> List[str]:
        """テンプレートファイルからブロック名を抽出"""
        try:
            with open(self.templates_dir / template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # {% block block_name %}パターンを検索
            block_pattern = r'{%\s*block\s+(\w+)\s*%}'
            blocks = re.findall(block_pattern, content)
            
            return blocks
            
        except Exception:
            return []
    
    def _analyze_template_inheritance(self, template_path: Path) -> Dict:
        """テンプレートの継承関係を解析"""
        try:
            with open(self.templates_dir / template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # {% extends "parent.html" %}パターンを検索
            extends_pattern = r'{%\s*extends\s+["\']([^"\']+)["\']\s*%}'
            extends_match = re.search(extends_pattern, content)
            
            parent_template = extends_match.group(1) if extends_match else None
            blocks = self._get_template_blocks(template_path)
            
            return {
                'parent_template': parent_template,
                'blocks': blocks
            }
            
        except Exception:
            return {
                'parent_template': None,
                'blocks': []
            }
    
    def _check_block_consistency(self, child_path: Path, parent_path: str, 
                                parent_blocks: List[str], child_blocks: List[str]) -> List[InheritanceError]:
        """親子テンプレート間のブロック整合性をチェック"""
        errors = []
        
        # 子テンプレートで定義されているが親テンプレートに存在しないブロック
        extra_blocks = set(child_blocks) - set(parent_blocks)
        
        if extra_blocks:
            errors.append(InheritanceError(
                template_path=str(child_path),
                parent_template=parent_path,
                error_type="ExtraBlocks",
                message=f"親テンプレートに存在しないブロックが定義されています",
                extra_blocks=list(extra_blocks)
            ))
        
        return errors
    
    def _get_syntax_suggestion(self, error_message: str) -> Optional[str]:
        """構文エラーに対する修正提案を生成"""
        suggestions = {
            "unexpected 'end of template'": "ブロックまたはタグが正しく閉じられていません。{% endblock %}や{% endif %}を確認してください。",
            "expected token 'end of statement block'": "ステートメントブロックが正しく閉じられていません。%}を確認してください。",
            "unexpected char": "予期しない文字があります。テンプレート構文を確認してください。",
            "expected token": "トークンが不足しています。構文を確認してください。"
        }
        
        for pattern, suggestion in suggestions.items():
            if pattern in error_message.lower():
                return suggestion
        
        return "テンプレート構文を確認してください。"
    
    def _get_default_context(self) -> Dict:
        """テンプレートレンダリング用のデフォルトコンテキスト"""
        # Mock request object
        class MockRequest:
            def __init__(self):
                self.endpoint = 'main.dashboard'
                self.url = '/'
                self.method = 'GET'
                self.args = {}
                self.form = {}
        
        return {
            'url_for': lambda endpoint, **values: f"/{endpoint.replace('.', '/')}",
            'get_flashed_messages': lambda **kwargs: [],
            'request': MockRequest(),
            'stats': {
                'total_projects': 0,
                'total_revenue': 0,
                'total_expenses': 0,
                'total_gross_profit': 0,
                'current_year': 2024
            },
            'available_years': [2024, 2023, 2022],
            'recent_projects': [],
            'projects': [],
            'branches': [],
            'config': {
                'SECRET_KEY': 'test-key'
            }
        }