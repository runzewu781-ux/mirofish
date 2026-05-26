"""
Vercel Serverless 入口 — Flask 应用
"""
from backend.app import create_app

app = create_app()
