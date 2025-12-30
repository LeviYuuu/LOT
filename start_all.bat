@echo off
chcp 65001 >nul
echo ========================================
echo   启动IoT项目（发布端 + 订阅端）
echo ========================================
echo.
cd /d %~dp0

echo 正在启动订阅端...
start "订阅端 - 端口5001" cmd /k "python subscribe_app.py"

timeout /t 3 /nobreak >nul

echo 正在启动发布端...
start "发布端 - 端口5000" cmd /k "python publish_app.py"

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo 订阅端: http://127.0.0.1:5001/
echo 发布端: http://127.0.0.1:5000/
echo.
echo 两个窗口已打开，关闭窗口即可停止服务
echo.
pause


