"""
股票监控系统 - 简单启动器
"""
import sys
import os
import webbrowser
import time
from threading import Timer

# 设置环境
os.environ['FLASK_ENV'] = 'production'

# 导入Flask应用
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app import app


def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:8000')


if __name__ == '__main__':
    print('================================')
    print('股票监控系统')
    print('================================')
    print('')
    print('服务启动中...')
    print('访问地址: http://127.0.0.1:8000')
    print('')
    print('关闭此窗口将停止服务')
    print('')
    
    # 启动浏览器
    Timer(2, open_browser).start()
    
    # 启动Flask
    app.run(host='0.0.0.0', port=8000, debug=False)

