"""
WSGI 入口文件 — 供 Gunicorn / Render 使用

启动命令:
    gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2
"""

import os
import sys

# 确保当前目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Render 等 PaaS 平台通常注入 PORT 环境变量
port = int(os.environ.get('PORT', os.environ.get('FLASK_PORT', 5001)))
os.environ.setdefault('FLASK_PORT', str(port))

application = create_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=port)
