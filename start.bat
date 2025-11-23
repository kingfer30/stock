@echo off
echo ====================================
echo 股市实时监控看板 - 启动脚本
echo ====================================
echo.

echo [1/4] 检查 Python 环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo.
echo [2/4] 启动后端服务...
start "后端服务" cmd /k "cd backend && pip install -r requirements.txt && python app.py"

timeout /t 3 /nobreak >nul

echo.
echo [3/4] 检查 Node.js 环境...
node --version
if %errorlevel% neq 0 (
    echo 错误: 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

echo.
echo [4/4] 启动前端服务...
start "前端服务" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ====================================
echo 启动完成！
echo 后端服务: http://localhost:5000
echo 前端服务: http://localhost:3000
echo ====================================
echo.
echo 按任意键关闭此窗口...
pause >nul

