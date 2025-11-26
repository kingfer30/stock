"""
股票监控系统 - 启动器
用于PyInstaller打包
"""
import sys
import os
import webbrowser
import time
from threading import Timer
import socket

# 获取可执行文件目录
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 设置静态文件路径
static_folder = os.path.join(BASE_DIR, 'backend', 'static')

# 导入Flask
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))
os.environ['FLASK_ENV'] = 'production'

# 禁用Flask开发服务器警告
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from flask import Flask, send_from_directory
from flask_cors import CORS
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 导入路由
from routes.trade_dates import trade_dates_bp
from routes.market_data import market_data_bp
from routes.lianban_data import lianban_data_bp
from routes.max_volume import max_volume_bp
from routes.next_day_jingjia import next_day_jingjia_bp

# 创建Flask应用
app = Flask(__name__, static_folder=static_folder, static_url_path='')
CORS(app)

# 注册路由
app.register_blueprint(trade_dates_bp)
app.register_blueprint(market_data_bp)
app.register_blueprint(lianban_data_bp)
app.register_blueprint(max_volume_bp)
app.register_blueprint(next_day_jingjia_bp)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve静态文件"""
    if path.startswith('api/'):
        return {"error": "Not found"}, 404
    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')


def find_free_port():
    """查找可用端口"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def open_browser(port):
    """延迟打开浏览器"""
    time.sleep(2)
    try:
        webbrowser.open(f'http://127.0.0.1:{port}')
    except:
        pass


if __name__ == '__main__':
    # 查找可用端口
    port = 8000
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            port = find_free_port()
        sock.close()
    except:
        pass

    print('================================')
    print('    股票监控系统    ')
    print('================================')
    print(f'服务地址: http://127.0.0.1:{port}')
    print('正在启动浏览器...')
    print('')
    print('提示: 关闭此窗口将停止服务')
    print('================================')
    print('')

    # 启动浏览器
    Timer(2, open_browser, args=(port,)).start()

    # 启动Flask
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print('\n服务已停止')
    except Exception as e:
        print(f'\n错误: {e}')
        input('按回车键退出...')

