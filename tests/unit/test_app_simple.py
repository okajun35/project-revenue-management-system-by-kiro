#!/usr/bin/env python3
"""
Simple Flask app test without SQLAlchemy to verify template rendering
"""
from flask import Flask, render_template
import os

# Flaskアプリを作成し、テンプレートディレクトリを明示的に指定
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='static')

@app.route('/')
def dashboard():
    """Test dashboard route"""
    # Mock data for testing
    stats = {
        'total_projects': 5,
        'total_revenue': 1500000.0,
        'total_expenses': 900000.0,
        'total_gross_profit': 600000.0
    }
    
    # Mock recent projects
    recent_projects = [
        {
            'project_name': 'テストプロジェクト1',
            'project_code': 'TEST001',
            'revenue': 500000
        },
        {
            'project_name': 'テストプロジェクト2', 
            'project_code': 'TEST002',
            'revenue': 750000
        }
    ]
    
    return render_template('dashboard_test.html', stats=stats, recent_projects=recent_projects)

@app.route('/health')
def health():
    """Simple health check"""
    return {'status': 'ok', 'message': 'Template system working'}

if __name__ == '__main__':
    print("Starting simple Flask app to test templates...")
    print("Visit http://localhost:5000 to see the dashboard")
    app.run(debug=True, port=5000)