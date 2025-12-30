@echo off
chcp 65001 >nul
echo ========================================
echo   启动发布端应用
echo ========================================
echo.
cd /d %~dp0
echo 当前目录: %CD%
echo.
echo 正在启动发布端...
echo 访问地址: http://127.0.0.1:5000/
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.
python publish_app.py
pause


