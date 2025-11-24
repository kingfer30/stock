"""分时最大成交量接口"""
from flask import Blueprint, jsonify, request
import requests
from utils import get_field_by_keyword

max_volume_bp = Blueprint('max_volume', __name__)


@max_volume_bp.route('/api/max-volume', methods=['POST'])
def fetch_max_volume():
    """获取单个股票的分时最大成交量"""
    try:
        data = request.get_json()
        stock_name = data.get('stock_name')
        query_date = data.get('query_date')
        
        # 格式化日期为x年x月x日
        year = query_date[:4]
        month = query_date[4:6]
        day = query_date[6:]
        date_str = f"{year}年{month}月{day}日"
        
        # 构建查询语句
        max_vol_query = f"{date_str}{stock_name}分时最大成交量"
        
        # 请求分时最大成交量数据
        response = requests.get(
            f"https://ai.iwencai.com/urp/v7/index/robot-index?uuid=23225&query={max_vol_query}",
            timeout=15,
            verify=False,
            headers={
                "Host": "ai.iwencai.com",
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "lhb/5.17.9 (xxxxx; build:0; iOS 16.6.0) Alamofire/4.9.1",
            },
        )
        
        if response.status_code == 200:
            max_vol_json = response.json()
            if max_vol_json.get("status_code") == "0":
                max_vol_datas = max_vol_json["answer"]["components"][0]["data"].get("datas", [])
                if max_vol_datas:
                    first_item = max_vol_datas[0]
                    max_vol_field = get_field_by_keyword(first_item, f"最大一分钟成交量[{query_date}]") or get_field_by_keyword(first_item, "最大一分钟成交量")
                    if max_vol_field:
                        try:
                            formatted_vol = f"{float(max_vol_field)/10000:.2f}"
                            return jsonify({"success": True, "volume": formatted_vol})
                        except:
                            return jsonify({"success": True, "volume": str(max_vol_field)})
        
        return jsonify({"success": False, "error": "未获取到数据"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

