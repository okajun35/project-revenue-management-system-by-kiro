#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from app.models import Branch
from app import db

def fix_osaka_branch():
    app = create_app()
    
    with app.app_context():
        print('=== 大阪支社をアクティブに変更 ===')
        osaka_branch = Branch.query.filter_by(branch_name='大阪支社').first()
        
        if osaka_branch:
            print(f'変更前: {osaka_branch.branch_name} - Active: {osaka_branch.is_active}')
            osaka_branch.is_active = True
            db.session.commit()
            print(f'変更後: {osaka_branch.branch_name} - Active: {osaka_branch.is_active}')
            
            print('\n=== 変更後のアクティブ支社一覧 ===')
            active_branches = Branch.get_active_branches()
            for branch in active_branches:
                print(f'ID: {branch.id}, Name: {branch.branch_name}')
        else:
            print('大阪支社が見つかりません')

if __name__ == '__main__':
    fix_osaka_branch()