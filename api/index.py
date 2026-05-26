"""
Vercel Serverless 入口 — Flask 应用
"""
import sys
import os

# Vercel 只读文件系统兼容：使所有 os.makedirs 调用在只读环境下不崩溃
_original_makedirs = os.makedirs


def _safe_makedirs(name, mode=0o777, exist_ok=False):
    try:
        _original_makedirs(name, mode, exist_ok=True)
    except OSError:
        pass


os.makedirs = _safe_makedirs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app import create_app
app = create_app()
