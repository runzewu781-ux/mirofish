@echo off
chcp 65001 >nul
echo ==========================================
echo   Public Opinion Forecasting - 启动服务
echo ==========================================
echo.

cd /d "%~dp0backend"

REM 检查 .env 文件
if not exist "..\.env" (
    echo [警告] 未找到 .env 文件，使用默认配置
    echo        建议复制 .env.example 为 .env 并填入 API Key
    echo.
)

REM 检查虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo [1/2] 激活虚拟环境...
    call .venv\Scripts\activate.bat
) else (
    echo [1/2] 未找到虚拟环境，使用系统 Python...
)

echo [2/2] 启动 Flask 后端...
echo.
echo 服务启动后访问: http://localhost:5001
echo 按 Ctrl+C 停止服务
echo ==========================================
python run.py
pause
