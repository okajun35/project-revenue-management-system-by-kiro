#!/usr/bin/env python3
"""
プロジェクト収支システム - テスト用サンプルデータ
"""

from datetime import datetime, date
from app.enums import OrderProbability, ProjectStatus

# 支社データ
SAMPLE_BRANCHES = [
    {
        'id': 1,
        'name': '東京本社',
        'code': 'TKY',
        'address': '東京都千代田区丸の内1-1-1',
        'phone': '03-1234-5678',
        'manager': '田中太郎',
        'created_at': datetime(2023, 1, 1, 9, 0, 0),
        'updated_at': datetime(2023, 1, 1, 9, 0, 0)
    },
    {
        'id': 2,
        'name': '大阪支社',
        'code': 'OSK',
        'address': '大阪府大阪市北区梅田1-1-1',
        'phone': '06-1234-5678',
        'manager': '佐藤花子',
        'created_at': datetime(2023, 1, 15, 10, 0, 0),
        'updated_at': datetime(2023, 1, 15, 10, 0, 0)
    },
    {
        'id': 3,
        'name': '名古屋支社',
        'code': 'NGY',
        'address': '愛知県名古屋市中区栄1-1-1',
        'phone': '052-1234-5678',
        'manager': '鈴木一郎',
        'created_at': datetime(2023, 2, 1, 11, 0, 0),
        'updated_at': datetime(2023, 2, 1, 11, 0, 0)
    },
    {
        'id': 4,
        'name': '福岡支社',
        'code': 'FKO',
        'address': '福岡県福岡市博多区博多駅前1-1-1',
        'phone': '092-1234-5678',
        'manager': '高橋次郎',
        'created_at': datetime(2023, 3, 1, 12, 0, 0),
        'updated_at': datetime(2023, 3, 1, 12, 0, 0)
    }
]

# 年度データ
SAMPLE_FISCAL_YEARS = [
    {
        'id': 1,
        'year': 2023,
        'start_date': date(2023, 4, 1),
        'end_date': date(2024, 3, 31),
        'is_active': False,
        'created_at': datetime(2023, 4, 1, 9, 0, 0),
        'updated_at': datetime(2023, 4, 1, 9, 0, 0)
    },
    {
        'id': 2,
        'year': 2024,
        'start_date': date(2024, 4, 1),
        'end_date': date(2025, 3, 31),
        'is_active': True,
        'created_at': datetime(2024, 4, 1, 9, 0, 0),
        'updated_at': datetime(2024, 4, 1, 9, 0, 0)
    },
    {
        'id': 3,
        'year': 2025,
        'start_date': date(2025, 4, 1),
        'end_date': date(2026, 3, 31),
        'is_active': False,
        'created_at': datetime(2025, 4, 1, 9, 0, 0),
        'updated_at': datetime(2025, 4, 1, 9, 0, 0)
    }
]

# プロジェクトデータ
SAMPLE_PROJECTS = [
    {
        'id': 1,
        'code': 'PRJ001',
        'name': 'Webシステム開発プロジェクト',
        'branch_id': 1,
        'fiscal_year': 2024,
        'order_probability': OrderProbability.HIGH.value,
        'status': ProjectStatus.IN_PROGRESS.value,
        'revenue': 5000000,
        'expenses': 3500000,
        'gross_profit': 1500000,
        'start_date': date(2024, 4, 1),
        'end_date': date(2024, 12, 31),
        'client_name': 'ABC株式会社',
        'description': 'ECサイトの新規開発プロジェクト',
        'created_at': datetime(2024, 4, 1, 9, 0, 0),
        'updated_at': datetime(2024, 4, 1, 9, 0, 0)
    },
    {
        'id': 2,
        'code': 'PRJ002',
        'name': 'モバイルアプリ開発',
        'branch_id': 2,
        'fiscal_year': 2024,
        'order_probability': OrderProbability.MEDIUM.value,
        'status': ProjectStatus.IN_PROGRESS.value,
        'revenue': 3000000,
        'expenses': 2200000,
        'gross_profit': 800000,
        'start_date': date(2024, 5, 1),
        'end_date': date(2024, 10, 31),
        'client_name': 'XYZ商事',
        'description': 'iOS/Androidアプリの開発',
        'created_at': datetime(2024, 5, 1, 10, 0, 0),
        'updated_at': datetime(2024, 5, 1, 10, 0, 0)
    },
    {
        'id': 3,
        'code': 'PRJ003',
        'name': 'データ分析システム',
        'branch_id': 1,
        'fiscal_year': 2024,
        'order_probability': OrderProbability.HIGH.value,
        'status': ProjectStatus.COMPLETED.value,
        'revenue': 8000000,
        'expenses': 5500000,
        'gross_profit': 2500000,
        'start_date': date(2024, 1, 1),
        'end_date': date(2024, 6, 30),
        'client_name': '株式会社データテック',
        'description': 'ビッグデータ分析基盤の構築',
        'created_at': datetime(2024, 1, 1, 9, 0, 0),
        'updated_at': datetime(2024, 6, 30, 17, 0, 0)
    },
    {
        'id': 4,
        'code': 'PRJ004',
        'name': 'クラウド移行プロジェクト',
        'branch_id': 3,
        'fiscal_year': 2024,
        'order_probability': OrderProbability.LOW.value,
        'status': ProjectStatus.PLANNING.value,
        'revenue': 12000000,
        'expenses': 8000000,
        'gross_profit': 4000000,
        'start_date': date(2024, 7, 1),
        'end_date': date(2025, 3, 31),
        'client_name': 'グローバル製造株式会社',
        'description': 'オンプレミスからクラウドへの移行',
        'created_at': datetime(2024, 6, 15, 14, 0, 0),
        'updated_at': datetime(2024, 6, 15, 14, 0, 0)
    },
    {
        'id': 5,
        'code': 'PRJ005',
        'name': 'セキュリティ強化プロジェクト',
        'branch_id': 4,
        'fiscal_year': 2024,
        'order_probability': OrderProbability.MEDIUM.value,
        'status': ProjectStatus.IN_PROGRESS.value,
        'revenue': 4500000,
        'expenses': 3200000,
        'gross_profit': 1300000,
        'start_date': date(2024, 3, 1),
        'end_date': date(2024, 9, 30),
        'client_name': '金融サービス株式会社',
        'description': 'セキュリティ監査とシステム強化',
        'created_at': datetime(2024, 3, 1, 11, 0, 0),
        'updated_at': datetime(2024, 3, 1, 11, 0, 0)
    },
    {
        'id': 6,
        'code': 'PRJ006',
        'name': 'AI導入支援プロジェクト',
        'branch_id': 1,
        'fiscal_year': 2025,
        'order_probability': OrderProbability.HIGH.value,
        'status': ProjectStatus.PLANNING.value,
        'revenue': 15000000,
        'expenses': 10000000,
        'gross_profit': 5000000,
        'start_date': date(2025, 4, 1),
        'end_date': date(2026, 3, 31),
        'client_name': 'テクノロジー株式会社',
        'description': '機械学習システムの導入と運用支援',
        'created_at': datetime(2024, 12, 1, 9, 0, 0),
        'updated_at': datetime(2024, 12, 1, 9, 0, 0)
    },
    {
        'id': 7,
        'code': 'PRJ007',
        'name': 'レガシーシステム刷新',
        'branch_id': 2,
        'fiscal_year': 2023,
        'order_probability': OrderProbability.HIGH.value,
        'status': ProjectStatus.COMPLETED.value,
        'revenue': 20000000,
        'expenses': 14000000,
        'gross_profit': 6000000,
        'start_date': date(2023, 4, 1),
        'end_date': date(2024, 3, 31),
        'client_name': '老舗製造業株式会社',
        'description': '30年前のシステムを最新技術で刷新',
        'created_at': datetime(2023, 4, 1, 9, 0, 0),
        'updated_at': datetime(2024, 3, 31, 17, 0, 0)
    },
    {
        'id': 8,
        'code': 'PRJ008',
        'name': 'IoTプラットフォーム構築',
        'branch_id': 3,
        'fiscal_year': 2024,
        'order_probability': OrderProbability.MEDIUM.value,
        'status': ProjectStatus.IN_PROGRESS.value,
        'revenue': 7500000,
        'expenses': 5200000,
        'gross_profit': 2300000,
        'start_date': date(2024, 6, 1),
        'end_date': date(2025, 2, 28),
        'client_name': 'スマート工場株式会社',
        'description': 'IoTデバイス管理プラットフォームの開発',
        'created_at': datetime(2024, 6, 1, 10, 0, 0),
        'updated_at': datetime(2024, 6, 1, 10, 0, 0)
    },
    {
        'id': 9,
        'code': 'PRJ009',
        'name': 'ブロックチェーン実証実験',
        'branch_id': 4,
        'fiscal_year': 2024,
        'order_probability': OrderProbability.LOW.value,
        'status': ProjectStatus.PLANNING.value,
        'revenue': 6000000,
        'expenses': 4500000,
        'gross_profit': 1500000,
        'start_date': date(2024, 10, 1),
        'end_date': date(2025, 3, 31),
        'client_name': 'フィンテック株式会社',
        'description': 'ブロックチェーン技術の実証実験',
        'created_at': datetime(2024, 9, 1, 14, 0, 0),
        'updated_at': datetime(2024, 9, 1, 14, 0, 0)
    },
    {
        'id': 10,
        'code': 'PRJ010',
        'name': 'デジタル変革コンサルティング',
        'branch_id': 1,
        'fiscal_year': 2024,
        'order_probability': OrderProbability.HIGH.value,
        'status': ProjectStatus.IN_PROGRESS.value,
        'revenue': 9000000,
        'expenses': 6300000,
        'gross_profit': 2700000,
        'start_date': date(2024, 2, 1),
        'end_date': date(2024, 11, 30),
        'client_name': '伝統企業株式会社',
        'description': 'デジタル変革戦略の策定と実行支援',
        'created_at': datetime(2024, 2, 1, 9, 0, 0),
        'updated_at': datetime(2024, 2, 1, 9, 0, 0)
    }
]

# 統計データ用の集計情報
SAMPLE_STATISTICS = {
    'total_projects': len(SAMPLE_PROJECTS),
    'total_revenue': sum(p['revenue'] for p in SAMPLE_PROJECTS),
    'total_expenses': sum(p['expenses'] for p in SAMPLE_PROJECTS),
    'total_gross_profit': sum(p['gross_profit'] for p in SAMPLE_PROJECTS),
    'projects_by_year': {
        2023: [p for p in SAMPLE_PROJECTS if p['fiscal_year'] == 2023],
        2024: [p for p in SAMPLE_PROJECTS if p['fiscal_year'] == 2024],
        2025: [p for p in SAMPLE_PROJECTS if p['fiscal_year'] == 2025]
    },
    'projects_by_branch': {
        1: [p for p in SAMPLE_PROJECTS if p['branch_id'] == 1],
        2: [p for p in SAMPLE_PROJECTS if p['branch_id'] == 2],
        3: [p for p in SAMPLE_PROJECTS if p['branch_id'] == 3],
        4: [p for p in SAMPLE_PROJECTS if p['branch_id'] == 4]
    },
    'projects_by_status': {
        'planning': [p for p in SAMPLE_PROJECTS if p['status'] == ProjectStatus.PLANNING.value],
        'in_progress': [p for p in SAMPLE_PROJECTS if p['status'] == ProjectStatus.IN_PROGRESS.value],
        'completed': [p for p in SAMPLE_PROJECTS if p['status'] == ProjectStatus.COMPLETED.value]
    }
}