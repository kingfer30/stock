"""市场数据接口"""
from flask import Blueprint, jsonify, request
import requests
from datetime import datetime
import time
from utils import get_field_by_keyword

market_data_bp = Blueprint('market_data', __name__)

# 配置请求参数
BASE_URL = "https://apphwshhq.longhuvip.com/w1/api/index.php?time=" + time.ctime()

HEADERS = {
    "Host": "apphwshhq.longhuvip.com",
    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; 2210132C Build/PQ3A.190605.08141016)",
    "Accept": "*/*",
    "Accept-Language": "zh-Hans-CN;q=1.0",
    "Accept-Encoding": "gzip;q=1.0, compress;q=0.5",
    "Connection": "keep-alive",
}

FORM_DATA = {
    "PhoneOSNew": 2,
    "VerSion": "5.17.0.9",
    "View": "2,4,5,7,10",
    "a": "GetInfo",
    "apiv": "w38",
    "c": "Index",
}


def parse_main_data(data):
    """解析主要市场数据"""
    try:
        parsed = {
            "bace_face_list": [],
            "da_ban_stats": {},
            "phb_list": [],
            "update_time": "未知",
            "day": "",
        }
        
        # 解析时间戳
        if "Time" in data:
            try:
                parsed["update_time"] = datetime.fromtimestamp(data["Time"]).strftime("%Y-%m-%d %H:%M:%S")
            except:
                parsed["update_time"] = "时间格式错误"
        
        if "Day" in data:
            parsed["day"] = data["Day"]
        
        # 解析BaceFaceList
        if "BaceFaceList" in data and isinstance(data["BaceFaceList"], list):
            for item in data["BaceFaceList"]:
                if len(item) >= 3:
                    parsed["bace_face_list"].append({
                        "name": str(item[0]),
                        "value": str(item[1]),
                        "id": str(item[2]),
                    })
        
        # 解析DaBanList
        if "DaBanList" in data and isinstance(data["DaBanList"], dict):
            try:
                t_feng_ban = float(data["DaBanList"].get("tFengBan", "0"))
                l_feng_ban = float(data["DaBanList"].get("lFengBan", "0"))
                po_ban_rate = f"{(100 - t_feng_ban):.2f}%"
                fengban_res = f"{t_feng_ban:.2f}% / {l_feng_ban:.2f}%"
            except:
                po_ban_rate = "0.00%"
                fengban_res = "0 / 0"
            
            try:
                zr_lb_j = float(data["DaBanList"].get("ZRLBJ", "0"))
                zr_lb_j_formatted = f"{zr_lb_j:.2f}%"
            except:
                zr_lb_j_formatted = "0.00%"
            
            parsed["da_ban_stats"] = {
                "zhangting": f"{data['DaBanList'].get('tZhangTing', '0')} / {data['DaBanList'].get('lZhangTing', '0')}",
                "fengban": fengban_res,
                "dieting": f"{data['DaBanList'].get('tDieTing', '0')} / {data['DaBanList'].get('lDieTing', '0')}",
                "zhangdie": f"{data['DaBanList'].get('SZJS', '0')} / {data['DaBanList'].get('PPJS', '0')} / {data['DaBanList'].get('XDJS', '0')}",
                "heat_index": data["DaBanList"].get("ZHQD", "0"),
                "poban_rate": po_ban_rate,
                "zrzt_jin": data["DaBanList"].get("ZRZTJ", "0"),
                "zrlb_jin": zr_lb_j_formatted,
                "sz_ln": data["DaBanList"].get("szln", "0"),
                "hs_ln": data["DaBanList"].get("qscln", "0"),
                "sz_zr_ln": data["DaBanList"].get("s_zrcs", "0"),
                "hs_zr_ln": data["DaBanList"].get("q_zrcs", "0"),
            }
        
        # 解析排行榜
        if "PHBList" in data and isinstance(data["PHBList"], list):
            for item in data["PHBList"]:
                if len(item) >= 6:
                    parsed["phb_list"].append({
                        "code": str(item[0]),
                        "name": str(item[1]),
                        "change": f"{float(item[2]):.2f}%" if isinstance(item[2], (int, float)) else str(item[2]),
                        "days": str(item[3]),
                        "type": str(item[4]),
                        "concept": str(item[5]),
                    })
        
        return parsed
    except Exception as e:
        print(f"数据解析失败: {str(e)}")
        return None


@market_data_bp.route('/api/market-data', methods=['POST'])
def fetch_market_data():
    """获取市场数据"""
    try:
        data = request.get_json()
        selected_date = data.get('selected_date')
        
        # 获取主数据
        response = requests.post(
            BASE_URL, data=FORM_DATA, headers=HEADERS, timeout=15, verify=False
        )
        
        if response.status_code != 200:
            return jsonify({"success": False, "error": f"接口返回异常状态码: {response.status_code}"})
        
        main_data = response.json()
        today = main_data.get("Day", "")
        if today == "":
            today = datetime.now().strftime("%Y-%m-%d")
        today = today.replace("-", "")
        
        # 用于查询的日期
        query_date = selected_date if selected_date else today
        
        # 获取竞价跌幅
        竞价跌幅 = []
        response = requests.get(
            "https://ai.iwencai.com/urp/v7/index/robot-index?uuid=23225&query=竞价涨幅低于-7%的同花顺行业且按照竞价涨幅小到大",
            timeout=15,
            verify=False,
            headers={
                "Host": "ai.iwencai.com",
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "lhb/5.17.9 (xxxxx; build:0; iOS 16.6.0) Alamofire/4.9.1",
            },
        )
        if response.status_code == 200:
            json_data = response.json()
            if json_data["status_code"] == "0":
                tmp = json_data["answer"]["components"][0]["data"]["datas"]
                for item in tmp:
                    jjzf = get_field_by_keyword(item, "竞价涨幅")
                    sjzf = get_field_by_keyword(item, "最新涨跌幅")
                    entry = {
                        "code": str(item.get("股票代码", "")),
                        "name": str(item.get("股票简称", "")),
                        "plate": str(item.get("所属同花顺行业", "")),
                        "jjzf": f"{float(jjzf):.2f}%" if jjzf else "",
                        "sjzf": f"{float(sjzf):.2f}%" if sjzf else "",
                    }
                    竞价跌幅.append(entry)
        
        # 获取竞价涨幅
        竞价涨幅 = []
        response = requests.get(
            "https://ai.iwencai.com/urp/v7/index/robot-index?uuid=23225&query=竞价涨幅大于3%的同花顺行业且昨日首板且非科创板且不包含北交所且非ST股且按竞价涨幅大到小排序且包含竞价金额且包含实际流通市值",
            timeout=15,
            verify=False,
            headers={
                "Host": "ai.iwencai.com",
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "lhb/5.17.9 (xxxxx; build:0; iOS 16.6.0) Alamofire/4.9.1",
            },
        )
        if response.status_code == 200:
            json_data = response.json()
            if json_data["status_code"] == "0":
                tmp = json_data["answer"]["components"][0]["data"]["datas"]
                for item in tmp:
                    jjzf = get_field_by_keyword(item, "竞价涨幅")
                    jjje = get_field_by_keyword(item, "竞价金额")
                    sjsz = get_field_by_keyword(item, "自由流通市值")
                    sjzf = get_field_by_keyword(item, "最新涨跌幅")
                    
                    entry = {
                        "code": str(item.get("股票代码", "")),
                        "name": str(item.get("股票简称", "")),
                        "plate": str(item.get("所属同花顺行业", "")),
                        "jjzf": f"{float(jjzf):.2f}%" if jjzf else "",
                        "sjzf": f"{float(sjzf):.2f}%" if sjzf else "",
                        "jjje": f"{float(jjje)/100000000:.2f}亿" if jjje else "",
                        "sjsz": f"{float(sjsz)/100000000:.2f}亿" if sjsz else "",
                    }
                    竞价涨幅.append(entry)
        
        # 解析主数据
        parsed_data = parse_main_data(main_data)
        
        return jsonify({
            "success": True,
            "data": {
                "main": parsed_data,
                "jingjiaDiefu": 竞价跌幅,
                "jingjiaZhangfu": 竞价涨幅,
                "queryDate": query_date
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

