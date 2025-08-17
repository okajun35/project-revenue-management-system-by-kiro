# プロジェクト収支システム - Makefile

.PHONY: help install dev prod test clean docker-dev docker-prod sample-data

# デフォルトターゲット
help:
	@echo "プロジェクト収支システム - 利用可能なコマンド:"
	@echo ""
	@echo "🚀 クイックスタート:"
	@echo "  make demo         - デモ環境を構築して起動（推奨）"
	@echo ""
	@echo "開発環境:"
	@echo "  make install      - 依存関係をインストール"
	@echo "  make dev          - 開発サーバーを起動"
	@echo "  make test         - テストを実行"
	@echo "  make setup-dev    - 開発環境初期セットアップ"
	@echo ""
	@echo "データ管理:"
	@echo "  make init-db      - データベースを初期化"
	@echo "  make sample-data  - 基本サンプルデータを作成"
	@echo "  make demo-data    - 豊富なデモデータを作成"
	@echo ""
	@echo "本番環境:"
	@echo "  make prod         - 本番サーバーを起動"
	@echo "  make setup-prod   - 本番環境初期セットアップ"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-dev   - Docker開発環境を起動"
	@echo "  make docker-prod  - Docker本番環境を起動"
	@echo "  make docker-test  - Dockerセットアップをテスト"
	@echo ""
	@echo "メンテナンス:"
	@echo "  make clean        - 一時ファイルを削除"
	@echo "  make backup       - データベースをバックアップ"
	@echo "  make restore      - データベースをリストア"
	@echo "  make health       - ヘルスチェック実行"

# 依存関係インストール
install:
	pip install -r requirements.txt
	@echo "✅ 依存関係のインストールが完了しました"

# 開発サーバー起動
dev:
	@echo "🚀 開発サーバーを起動中..."
	python app.py

# 本番サーバー起動
prod:
	@echo "🚀 本番サーバーを起動中..."
	gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

# テスト実行
test:
	@echo "🧪 テストを実行中..."
	python -m pytest tests/ -v

# テスト（カバレッジ付き）
test-coverage:
	@echo "🧪 テスト（カバレッジ付き）を実行中..."
	python -m pytest tests/ --cov=app --cov-report=html --cov-report=term

# 基本サンプルデータ作成
sample-data:
	@echo "📊 基本サンプルデータを作成中..."
	python scripts/init_sample_data.py

# 豊富なデモデータ作成
demo-data:
	@echo "🎭 豊富なデモデータを作成中..."
	python scripts/init_sample_data.py
	python scripts/create_sample_data.py
	python scripts/add_monthly_sample_data.py
	@echo "✅ デモデータ作成完了"

# デモ環境起動（データ作成 + サーバー起動）
demo:
	@echo "🎭 デモ環境を構築中..."
	make init-db
	make demo-data
	@echo "🚀 デモサーバーを起動中..."
	@echo "ブラウザで http://localhost:5000 にアクセスしてください"
	python app.py

# サンプルデータ削除
clear-sample-data:
	@echo "🧹 サンプルデータを削除中..."
	python scripts/create_sample_data.py clear

# Docker開発環境
docker-dev:
	@echo "🐳 Docker開発環境を起動中..."
	docker-compose -f docker/dev/docker-compose.dev.yml up -d
	@echo "✅ 開発環境が起動しました: http://localhost:5000"

# Docker本番環境
docker-prod:
	@echo "🐳 Docker本番環境を起動中..."
	docker-compose -f docker/prod/docker-compose.prod.yml up -d
	@echo "✅ 本番環境が起動しました: http://localhost"

# Dockerセットアップテスト
docker-test:
	@echo "🧪 Dockerセットアップをテスト中..."
	python tests/manual/debug/test_docker_setup.py

# Docker環境停止
docker-stop:
	@echo "🛑 Docker環境を停止中..."
	docker-compose -f docker/dev/docker-compose.dev.yml down
	docker-compose -f docker/prod/docker-compose.prod.yml down

# データベース初期化
init-db:
	@echo "🗄️ データベースを初期化中..."
	python scripts/init_db.py

# バックアップ作成
backup:
	@echo "💾 バックアップを作成中..."
	@if [ -f "scripts/backup.sh" ]; then \
		bash scripts/backup.sh; \
	else \
		python -c "import shutil; from datetime import datetime; shutil.copy('data/projects.db', f'backups/backup_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.db'); print('✅ バックアップ作成完了')"; \
	fi

# リストア（バックアップファイルを指定）
restore:
	@echo "📥 リストアを実行中..."
	@echo "使用方法: make restore BACKUP=backup_file.db"
	@if [ -z "$(BACKUP)" ]; then \
		echo "❌ バックアップファイルを指定してください: make restore BACKUP=backup_file.db"; \
		exit 1; \
	fi
	@if [ -f "scripts/restore.sh" ]; then \
		bash scripts/restore.sh $(BACKUP); \
	else \
		cp $(BACKUP) data/projects.db; \
		echo "✅ リストア完了"; \
	fi

# 一時ファイル削除
clean:
	@echo "🧹 一時ファイルを削除中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "✅ クリーンアップ完了"

# 開発環境セットアップ（初回用）
setup-dev:
	@echo "🔧 開発環境をセットアップ中..."
	make install
	make init-db
	make sample-data
	@echo "✅ 開発環境セットアップ完了"
	@echo "次のコマンドで開発サーバーを起動: make dev"

# 本番環境セットアップ（初回用）
setup-prod:
	@echo "🔧 本番環境をセットアップ中..."
	make install
	make init-db
	@echo "✅ 本番環境セットアップ完了"
	@echo "サンプルデータが必要な場合: make sample-data"
	@echo "本番サーバー起動: make prod"

# ログ確認
logs:
	@echo "📋 ログを確認中..."
	@if [ -f "app.log" ]; then \
		tail -f app.log; \
	else \
		echo "ログファイルが見つかりません"; \
	fi

# Docker ログ確認
docker-logs:
	@echo "📋 Dockerログを確認中..."
	docker-compose -f docker/prod/docker-compose.prod.yml logs -f

# システム状態確認
status:
	@echo "📊 システム状態を確認中..."
	@echo "データベースファイル:"
	@ls -la data/ 2>/dev/null || echo "  データディレクトリが見つかりません"
	@echo ""
	@echo "Dockerコンテナ:"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  Dockerが起動していません"
	@echo ""
	@echo "プロセス:"
	@ps aux | grep -E "(python|gunicorn)" | grep -v grep || echo "  Pythonプロセスが見つかりません"

# ヘルスチェック
health:
	@echo "🏥 ヘルスチェックを実行中..."
	@curl -f http://localhost:5000/health 2>/dev/null && echo "✅ アプリケーション正常" || echo "❌ アプリケーション異常"
	@curl -f http://localhost/health 2>/dev/null && echo "✅ Nginx経由アクセス正常" || echo "⚠️ Nginx経由アクセス不可"