"""
Vercel Serverless 入口 — Flask 应用
"""
import sys
import os
import traceback

# 确保 backend 目录在 sys.path 中（用于内部绝对导入）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from backend.app import create_app as _create_app
    app = _create_app()
except Exception:
    from flask import Flask
    app = Flask(__name__)

    @app.route('/health')
    def health():
        return {'status': 'ok'}

    @app.route('/debug')
    def debug():
        return {
            'error': traceback.format_exc(),
            'cwd': os.getcwd(),
            'file': __file__,
            'sys_path': sys.path[:5],
        }
