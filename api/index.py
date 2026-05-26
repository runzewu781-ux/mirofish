"""
Vercel Serverless 入口 — 最小测试
"""
import sys
import os
import traceback


def create_test_app():
    from flask import Flask
    app = Flask(__name__)

    @app.route('/health')
    def health():
        return {'status': 'ok'}

    @app.route('/debug')
    def debug():
        backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
        return {
            'cwd': os.getcwd(),
            'file_dir': os.path.dirname(__file__),
            'backend_path': backend_path,
            'backend_exists': os.path.exists(backend_path),
            'sys_path': sys.path[:5],
            'files_in_api': os.listdir(os.path.dirname(__file__)) if os.path.exists(os.path.dirname(__file__)) else [],
            'parent_files': os.listdir(os.path.join(os.path.dirname(__file__), '..')) if os.path.exists(os.path.join(os.path.dirname(__file__), '..')) else [],
        }

    return app


# Try real app first, fallback to test
try:
    from backend.app import create_app
    app = create_app()
except Exception as e:
    app = create_test_app()
