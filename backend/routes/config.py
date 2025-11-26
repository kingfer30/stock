"""配置接口 - 提供运行时配置"""
from flask import Blueprint, jsonify
import os
import json
import sys

config_bp = Blueprint('config', __name__)


def get_config_file_path():
    """获取配置文件路径"""
    # 如果是打包后的exe，配置文件在exe同目录下
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的路径
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境，配置文件在项目根目录
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    return os.path.join(base_path, 'config.json')


def load_config():
    """加载配置文件"""
    config_file = get_config_file_path()
    
    # 默认配置
    default_config = {
        "auto_refresh_interval": 20,  # 自动刷新间隔（秒）
        "max_retries": 3,             # 最大重试次数
        "request_timeout": 10         # 请求超时时间（秒）
    }
    
    # 如果配置文件存在，读取配置
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 合并用户配置和默认配置
                default_config.update(user_config)
        except Exception as e:
            print(f"警告: 读取配置文件失败: {e}，使用默认配置")
    else:
        # 如果配置文件不存在，创建默认配置文件
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"已创建默认配置文件: {config_file}")
        except Exception as e:
            print(f"警告: 创建配置文件失败: {e}")
    
    return default_config


@config_bp.route('/api/config', methods=['GET'])
def get_config():
    """获取配置"""
    try:
        import sys
        config = load_config()
        return jsonify({
            "success": True,
            "config": config,
            "config_file": get_config_file_path()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "config": {
                "auto_refresh_interval": 20,
                "max_retries": 3,
                "request_timeout": 10
            }
        })

