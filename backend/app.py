"""主应用文件 - 注册所有路由"""
from flask import Flask
from flask_cors import CORS
import urllib3

# 导入所有路由蓝图
from routes.trade_dates import trade_dates_bp
from routes.market_data import market_data_bp
from routes.lianban_data import lianban_data_bp
from routes.max_volume import max_volume_bp
from routes.next_day_jingjia import next_day_jingjia_bp

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 注册所有蓝图
app.register_blueprint(trade_dates_bp)
app.register_blueprint(market_data_bp)
app.register_blueprint(lianban_data_bp)
app.register_blueprint(max_volume_bp)
app.register_blueprint(next_day_jingjia_bp)


@app.route('/')
def index():
    """健康检查接口"""
    return {
        "status": "ok",
        "message": "股市实时监控看板API服务运行中",
        "version": "2.0.0"
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
