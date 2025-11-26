"""主应用文件 - 注册所有路由"""
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import urllib3
import os
from datetime import datetime

# 导入所有路由蓝图
from routes.trade_dates import trade_dates_bp
from routes.market_data import market_data_bp
from routes.lianban_data import lianban_data_bp
from routes.max_volume import max_volume_bp
from routes.next_day_jingjia import next_day_jingjia_bp
from routes.config import config_bp

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 静态文件目录（生产环境）
static_folder = os.path.join(os.path.dirname(__file__), 'static')

app = Flask(__name__, static_folder=static_folder, static_url_path='')
CORS(app)  # 允许跨域请求


# 检查程序有效期
@app.before_request
def check_expiration():
    """检查程序是否过期（仅对API接口生效）"""
    # 只对 /api/ 路径进行检查
    if request.path.startswith('/api/'):
        expire_date = datetime(2026, 12, 31, 23, 59, 59)
        now = datetime.now()
        if now > expire_date:
            return jsonify({
                "success": False,
                "error": "程序已过期，请联系开发者更新"
            }), 403


# 注册所有蓝图
app.register_blueprint(trade_dates_bp)
app.register_blueprint(market_data_bp)
app.register_blueprint(lianban_data_bp)
app.register_blueprint(max_volume_bp)
app.register_blueprint(next_day_jingjia_bp)
app.register_blueprint(config_bp)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """
    serve静态文件（生产环境）或健康检查（开发环境）
    """
    # 如果是API请求，不处理（由蓝图处理）
    if path.startswith('api/'):
        return {"error": "Not found"}, 404
    
    # 如果static目录存在（生产环境）
    if os.path.exists(static_folder):
        if path != "" and os.path.exists(os.path.join(static_folder, path)):
            return send_from_directory(static_folder, path)
        else:
            # SPA应用，返回index.html
            return send_from_directory(static_folder, 'index.html')
    else:
        # 开发环境，返回API信息
        return {
            "status": "ok",
            "message": "股市实时监控看板API服务运行中",
            "version": "2.0.0",
            "mode": "development"
        }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
