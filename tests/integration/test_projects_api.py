#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from app.models import Project, Branch
import json

def test_projects_api():
    app = create_app()
    
    with app.app_context():
        print('=== データベース確認 ===')
        projects = Project.query.all()
        branches = Branch.query.all()
        print(f'Total projects: {len(projects)}')
        print(f'Total branches: {len(branches)}')
        
        if len(projects) > 0:
            print('\n最初の3件のプロジェクト:')
            for i, project in enumerate(projects[:3]):
                print(f'  {i+1}. {project.project_code} - {project.project_name}')
                print(f'     支社: {project.branch.branch_name if project.branch else "None"}')
                print(f'     年度: {project.fiscal_year}')
    
    with app.test_client() as client:
        print('\n=== API テスト ===')
        
        # プロジェクト一覧ページ
        response = client.get('/projects/')
        print(f'Projects page status: {response.status_code}')
        
        # プロジェクト一覧API
        response = client.get('/projects/api/list?draw=1&start=0&length=10')
        print(f'Projects API status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.get_json()
            print(f'API Response:')
            print(f'  Draw: {data.get("draw", "N/A")}')
            print(f'  Total records: {data.get("recordsTotal", 0)}')
            print(f'  Filtered records: {data.get("recordsFiltered", 0)}')
            print(f'  Data rows: {len(data.get("data", []))}')
            
            if len(data.get('data', [])) > 0:
                print(f'  First row: {data["data"][0][:3]}')
            else:
                print('  No data rows returned')
        else:
            print(f'API Error: {response.get_data(as_text=True)[:500]}')

if __name__ == '__main__':
    test_projects_api()