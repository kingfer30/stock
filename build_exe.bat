@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================
echo 股票监控系统 - 打包为EXE
echo ================================
echo.

REM 设置颜色
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%错误: 未找到Python，请先安装Python 3.7+%NC%
    pause
    exit /b 1
)

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo %RED%错误: 未找到Node.js，请先安装Node.js%NC%
    pause
    exit /b 1
)

echo %GREEN%[1/6] 清理旧文件...%NC%
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"
if exist "backend\static" rd /s /q "backend\static"
echo 清理完成
echo.

echo %GREEN%[2/6] 构建前端...%NC%
cd frontend
call npm install
if errorlevel 1 (
    echo %RED%前端依赖安装失败%NC%
    cd ..
    pause
    exit /b 1
)

call npm run build
if errorlevel 1 (
    echo %RED%前端构建失败%NC%
    cd ..
    pause
    exit /b 1
)

REM 复制前端静态文件到backend
echo 复制前端文件到backend/static...
xcopy /E /I /Y dist ..\backend\static
cd ..
echo 前端构建完成
echo.

echo %GREEN%[3/6] 安装后端依赖...%NC%
cd backend
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo %RED%后端依赖安装失败%NC%
    cd ..
    pause
    exit /b 1
)

REM 安装PyInstaller
pip install pyinstaller
if errorlevel 1 (
    echo %RED%PyInstaller安装失败%NC%
    cd ..
    pause
    exit /b 1
)
echo 后端依赖安装完成
echo.

echo %GREEN%[4/6] 复制启动脚本...%NC%
cd ..

REM 使用现成的模板文件
if exist "launcher_simple.py" (
    copy /Y launcher_simple.py launcher.py
    echo 启动脚本复制完成
) else (
    echo %RED%错误: 未找到 launcher_simple.py%NC%
    pause
    exit /b 1
)
echo.

echo %GREEN%[5/6] 打包为EXE...%NC%
cd backend
call venv\Scripts\activate.bat

REM 使用PyInstaller打包
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "股票监控系统" ^
    --icon=NONE ^
    --add-data "..\\backend\\static;static" ^
    --add-data "..\\backend\\routes;routes" ^
    --add-data "..\\backend\\utils.py;." ^
    --hidden-import=flask ^
    --hidden-import=flask_cors ^
    --hidden-import=urllib3 ^
    --hidden-import=requests ^
    --hidden-import=utils ^
    ..\launcher.py

if errorlevel 1 (
    echo %RED%打包失败%NC%
    cd ..
    pause
    exit /b 1
)
cd ..
echo 打包完成
echo.

echo %GREEN%[6/6] 整理输出文件...%NC%
REM 移动exe到根目录
if exist "backend\dist\股票监控系统.exe" (
    move /Y "backend\dist\股票监控系统.exe" "股票监控系统.exe"
    echo.
    echo ================================
    echo %GREEN%打包成功！%NC%
    echo ================================
    echo.
    echo 输出文件: 股票监控系统.exe
    echo 文件大小: 
    dir "股票监控系统.exe" | find "股票监控系统.exe"
    echo.
    echo 使用说明:
    echo 1. 双击 "股票监控系统.exe" 运行
    echo 2. 程序会自动打开浏览器
    echo 3. 关闭黑色窗口即可停止服务
    echo.
) else (
    echo %RED%未找到打包后的exe文件%NC%
    pause
    exit /b 1
)

REM 清理临时文件
echo 清理临时文件...
if exist "build" rd /s /q "build"
if exist "backend\build" rd /s /q "backend\build"
if exist "backend\dist" rd /s /q "backend\dist"
if exist "launcher.spec" del /f /q "launcher.spec"
if exist "backend\launcher.spec" del /f /q "backend\launcher.spec"
if exist "launcher.py" del /f /q "launcher.py"

echo.
echo %GREEN%完成！可以分发 "股票监控系统.exe" 给其他人使用%NC%
echo.
pause

