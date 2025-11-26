@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================
echo 股票监控系统 - 高级打包
echo ================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python
    pause
    exit /b 1
)

echo [1/7] 清理旧文件...
if exist "dist_app" rd /s /q "dist_app"
if exist "build" rd /s /q "build"
if exist "backend\static" rd /s /q "backend\static"
mkdir dist_app
echo 完成
echo.

echo [2/7] 构建前端...
cd frontend
call npm install
call npm run build
xcopy /E /I /Y dist ..\backend\static
cd ..
echo 完成
echo.

echo [3/7] 准备后端环境...
cd backend
if not exist "venv" python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
pip install pyinstaller
echo 完成
echo.

echo [4/7] 复制启动器模板...
cd ..

REM 使用现成的模板文件
if exist "launcher_template.py" (
    copy /Y launcher_template.py launcher_advanced.py
    echo 完成
) else (
    echo %RED%错误: 未找到 launcher_template.py%NC%
    pause
    exit /b 1
)
echo.

echo [5/7] 创建PyInstaller配置...
cd backend
call venv\Scripts\activate.bat

REM 创建spec文件
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis^(
echo     ['..\\launcher_advanced.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[
echo         ^('..\\backend\\static', 'backend\\static'^),
echo         ^('..\\backend\\routes', 'backend\\routes'^),
echo         ^('..\\backend\\utils.py', 'backend'^),
echo     ],
echo     hiddenimports=[
echo         'flask',
echo         'flask_cors',
echo         'urllib3',
echo         'requests',
echo         'utils',
echo         'routes.trade_dates',
echo         'routes.market_data',
echo         'routes.lianban_data',
echo         'routes.max_volume',
echo         'routes.next_day_jingjia',
echo         'routes.config',
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='股票监控系统',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=True,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo ^)
) > stock_app.spec

echo 完成
echo.

echo [6/7] 执行打包（这可能需要几分钟）...
pyinstaller stock_app.spec

if errorlevel 1 (
    echo 打包失败
    cd ..
    pause
    exit /b 1
)

cd ..
echo 完成
echo.

echo [7/7] 整理文件...
if exist "backend\dist\股票监控系统.exe" (
    copy /Y "backend\dist\股票监控系统.exe" "dist_app\股票监控系统.exe"
    
    REM 创建使用说明
    (
        echo 股票监控系统 - 使用说明
        echo ================================
        echo.
        echo 使用方法:
        echo 1. 双击 "股票监控系统.exe" 启动程序
        echo 2. 程序会自动打开浏览器
        echo 3. 关闭命令窗口即可停止服务
        echo.
        echo 配置刷新时间:
        echo - 首次运行会在EXE同目录自动创建 config.json
        echo - 用记事本打开编辑 "auto_refresh_interval" 的值^(单位:秒^)
        echo - 修改后重启程序即可生效
        echo - 示例: "auto_refresh_interval": 30  ^(30秒刷新一次^)
        echo.
        echo 注意事项:
        echo - 首次运行可能需要防火墙授权
        echo - 如果8000端口被占用，会自动使用其他端口
        echo - 程序运行时不要关闭黑色命令窗口
        echo.
        echo 系统要求:
        echo - Windows 7 及以上
        echo - 无需安装Python或Node.js
        echo.
        echo 访问地址: http://127.0.0.1:8000
        echo.
    ) > "dist_app\使用说明.txt"
    
    echo.
    echo ================================
    echo    打包成功！
    echo ================================
    echo.
    echo 输出目录: dist_app\
    echo 主程序: 股票监控系统.exe
    echo.
    dir "dist_app\股票监控系统.exe" | find "股票监控系统.exe"
    echo.
    echo 可以将 dist_app 目录下的所有文件分发给用户
    echo.
) else (
    echo 错误: 未找到生成的exe文件
    pause
    exit /b 1
)

REM 清理临时文件
echo 清理临时文件...
if exist "build" rd /s /q "build"
if exist "backend\build" rd /s /q "backend\build"
if exist "backend\dist" rd /s /q "backend\dist"
if exist "backend\stock_app.spec" del /f /q "backend\stock_app.spec"
if exist "launcher_advanced.py" del /f /q "launcher_advanced.py"

echo.
echo 打包完成！
echo.
pause

