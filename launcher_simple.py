"""
股票监控系统 - 简单启动器
"""
import sys
import os
import webbrowser
import time
import json
from threading import Timer

# 设置环境
os.environ['FLASK_ENV'] = 'production'

# 导入Flask应用
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app import app


def create_default_config():
    """在EXE同目录创建默认配置文件"""
    # 获取EXE所在目录
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后，使用exe所在目录
        base_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境，使用项目根目录
        base_dir = os.path.dirname(__file__)
    
    config_file = os.path.join(base_dir, 'config.json')
    
    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(config_file):
        default_config = {
            "auto_refresh_interval": 20
        }
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f'✅ 已创建配置文件: {config_file}')
        except Exception as e:
            print(f'⚠️  创建配置文件失败: {e}')
    else:
        print(f'✅ 配置文件已存在: {config_file}')


def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:8000')


if __name__ == '__main__':
    print('================================')
    print('股票监控系统')
    print('================================')
    print('')
    
    # 创建配置文件
    create_default_config()
    
    print('服务启动中...')
    print('访问地址: http://127.0.0.1:8000')
    print('')
    print('关闭此窗口将停止服务')
    print('================================')
    print('')
    
    # 启动浏览器
    Timer(2, open_browser).start()
    
    # 启动Flask
    app.run(host='0.0.0.0', port=8000, debug=False)

