"""交易日期接口"""
from flask import Blueprint, jsonify
import requests
from datetime import datetime

trade_dates_bp = Blueprint('trade_dates', __name__)


@trade_dates_bp.route('/api/trade-dates', methods=['GET'])
def get_trade_dates():
    """获取交易日期列表"""
    try:
        today = datetime.now().strftime("%Y%m%d")
        response = requests.get(
            f"https://data.10jqka.com.cn/dataapi/limit_up/trade_day?date={today}&stock=stock&next=10&prev=10",
            timeout=10,
            verify=False,
            headers={
                "Host": "data.10jqka.com.cn",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://data.10jqka.com.cn/",
            },
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("status_code") == 0:
                prev_dates = data["data"]["prev_dates"]  # 历史交易日
                next_dates = data["data"].get("next_dates", [])  # 未来交易日
                trade_day = data["data"].get("trade_day", False)  # 今天是否是交易日
                
                # 判断今天是否是交易日
                if trade_day:
                    # 今天是交易日，直接使用today
                    current_date = today
                else:
                    # 今天不是交易日，使用next_dates中最近的交易日
                    current_date = min(next_dates) if next_dates else (max(prev_dates) if prev_dates else today)
                
                # 构建日期列表：[当前交易日, 历史交易日...]（从新到旧）
                formatted_dates = []
                
                # 添加当前交易日
                try:
                    formatted = f"{current_date[:4]}-{current_date[4:6]}-{current_date[6:]}"
                    formatted_dates.append({"raw": current_date, "display": formatted, "is_current": True})
                except:
                    formatted_dates.append({"raw": current_date, "display": current_date, "is_current": True})
                
                # 添加历史交易日（从新到旧）
                for date_str in sorted(prev_dates, reverse=True):
                    # 避免重复添加当前日期
                    if date_str != current_date:
                        try:
                            formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                            formatted_dates.append({"raw": date_str, "display": formatted, "is_current": False})
                        except:
                            formatted_dates.append({"raw": date_str, "display": date_str, "is_current": False})
                
                return jsonify({"success": True, "data": formatted_dates, "current_date": current_date})
        return jsonify({"success": False, "error": "获取交易日期失败"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

