#!/usr/bin/env python3
"""
プロジェクト収支システム - メインアプリケーション
"""
import os
from app import create_app

# アプリケーションインスタンスを作成
app = create_app()

if __name__ == '__main__':
    # 開発サーバーとして実行
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development' or True  # 開発中は常にデバッグモード
    
    print(f"プロジェクト収支システムを起動中...")
    print(f"URL: http://localhost:{port}")
    print(f"デバッグモード: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)