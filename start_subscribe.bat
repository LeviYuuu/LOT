@echo off
chcp 65001 >nul
echo ========================================
echo   启动订阅端应用
echo ========================================
echo.
cd /d %~dp0
echo 当前目录: %CD%
echo.
echo 正在启动订阅端...
echo 访问地址: http://127.0.0.1:5001/
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.
python subscribe_app.py
pause


