#!/usr/bin/env python3
"""検索機能の手動テスト"""

from app import create_app

def run_test_server():
    app = create_app()
    app.config['DEBUG'] = True
    print("Starting test server...")
    print("Visit http://localhost:5000/projects/search to test search functionality")
    app.run(host='localhost', port=5000, debug=True)

if __name__ == "__main__":
    run_test_server()