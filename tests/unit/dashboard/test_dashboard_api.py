#!/usr/bin/env python3
"""
ダッシュボードAPIのテスト
"""

from app import create_app
import json

def test_dashboard_api():
    app = create_app()
    
    with app.test_client() as client:
        print('=== ダッシュボードAPIテスト ===')
        
        # ダッシュボード画面のテスト
        print('1. ダッシュボード画面のテスト')
        response = client.get('/')
        print(f'   ステータス: {response.status_code}')
        if response.status_code == 200:
            print('   ✓ ダッシュボード画面が正常に表示されました')
        else:
            print(f'   ✗ エラー: {response.data.decode()}')
        
        # 統計データAPIのテスト
        print('2. 統計データAPIのテスト')
        response = client.get('/api/dashboard-data')
        print(f'   ステータス: {response.status_code}')
        if response.status_code == 200:
            data = response.get_json()
            print(f'   ✓ 統計データ: プロジェクト数={data["total_projects"]}, 売上=¥{data["total_revenue"]:,.0f}')
        else:
            print(f'   ✗ エラー: {response.data.decode()}')
        
        # チャートデータAPIのテスト
        print('3. チャートデータAPIのテスト')
        response = client.get('/api/chart-data')
        print(f'   ステータス: {response.status_code}')
        if response.status_code == 200:
            data = response.get_json()
            print(f'   ✓ チャートデータ: 年度={data["years"]}, 売上={data["revenues"]}')
        else:
            print(f'   ✗ エラー: {response.data.decode()}')
        
        # 支社別統計APIのテスト
        print('4. 支社別統計APIのテスト')
        response = client.get('/api/branch-stats')
        print(f'   ステータス: {response.status_code}')
        if response.status_code == 200:
            data = response.get_json()
            print(f'   ✓ 支社別統計: {len(data["branch_stats"])}件の支社データ')
        else:
            print(f'   ✗ エラー: {response.data.decode()}')
        
        # 最近のプロジェクトAPIのテスト
        print('5. 最近のプロジェクトAPIのテスト')
        response = client.get('/api/recent-projects')
        print(f'   ステータス: {response.status_code}')
        if response.status_code == 200:
            data = response.get_json()
            print(f'   ✓ 最近のプロジェクト: {data["count"]}件')
        else:
            print(f'   ✗ エラー: {response.data.decode()}')
        
        # 受注角度分布APIのテスト
        print('6. 受注角度分布APIのテスト')
        response = client.get('/api/order-probability-distribution')
        print(f'   ステータス: {response.status_code}')
        if response.status_code == 200:
            data = response.get_json()
            print(f'   ✓ 受注角度分布: {len(data["distribution"])}種類の分布')
        else:
            print(f'   ✗ エラー: {response.data.decode()}')
        
        print('テスト完了')

if __name__ == '__main__':
    test_dashboard_api()