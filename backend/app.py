from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
from datetime import datetime
import urllib3
import time

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

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


# 辅助函数：通过关键字匹配获取字段值
def get_field_by_keyword(item_dict, keyword):
    """根据关键字匹配字段名并返回值"""
    for key in item_dict.keys():
        if keyword in key:
            return item_dict[key]
    return ""


@app.route('/api/trade-dates', methods=['GET'])
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
                prev_dates = data["data"]["prev_dates"]
                formatted_dates = []
                for date_str in reversed(prev_dates):
                    try:
                        formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                        formatted_dates.append({"raw": date_str, "display": formatted})
                    except:
                        formatted_dates.append({"raw": date_str, "display": date_str})
                return jsonify({"success": True, "data": formatted_dates})
        return jsonify({"success": False, "error": "获取交易日期失败"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/market-data', methods=['POST'])
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


@app.route('/api/lianban-data', methods=['POST'])
def fetch_lianban_data():
    """获取连板数据"""
    try:
        data = request.get_json()
        selected_date = data.get('selected_date')
        query_date = data.get('query_date')
        
        连板数据 = []
        
        # 构建查询语句
        if selected_date:
            date_formatted = f"{selected_date[:4]}-{selected_date[4:6]}-{selected_date[6:]}"
            query = f"非科创板且非st股{date_formatted}涨停且连板数大于等于1且含成交额且含涨停封单额且包含收盘价且包含成交量且包含自由流通股且包含自由流通市值且包含实际换手率且包含量比且{date_formatted}连续涨停天数从大到小排序"
        else:
            query = f"连板数大于等于1且非科创板且非st股且包含成交额且包含涨停封单额且包含收盘价且包含成交量且包含自由流通股且包含自由流通市值且包含实际换手率且包含量比且按连续涨停天数从大到小排序"
        
        response = requests.get(
            f"https://ai.iwencai.com/urp/v7/index/robot-index?uuid=23225&query={query}",
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
            if json_data.get("status_code") == "0":
                data_component = json_data["answer"]["components"][0]["data"]
                tmp = data_component.get("datas", [])
                total = data_component.get("meta", {}).get("total", 0)
                
                # 处理第一页数据
                if tmp:
                    for item in tmp:
                        entry = process_lianban_item(item, query_date)
                        连板数据.append(entry)
                
                # 处理分页
                current_count = len(tmp)
                if total > current_count:
                    page = 2
                    info = data_component.get("info", {})
                    
                    while current_count < total:
                        try:
                            page_response = requests.post(
                                "https://ms.10jqka.com.cn/gateway/urp/v7/landing/getDataList",
                                data={
                                    "query_type":"stock",
                                    "query": query,
                                    "perpage":15,
                                    "page": str(page),
                                    "info": json.dumps(info) if info else ""
                                },
                                headers={
                                    "Host": "ms.10jqka.com.cn",
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "User-Agent": "lhb/5.17.9 (xxxxx; build:0; iOS 16.6.0) Alamofire/4.9.1",
                                },
                                timeout=15,
                                verify=False,
                            )
                            
                            if page_response.status_code == 200:
                                page_json = page_response.json()
                                if page_json.get("status_code") == "0":
                                    page_datas = page_json["data"]["datas"]
                                    if not page_datas:
                                        break
                                    
                                    for item in page_datas:
                                        entry = process_lianban_item(item, query_date)
                                        连板数据.append(entry)
                                    
                                    current_count += len(page_datas)
                                    page += 1
                                else:
                                    break
                            else:
                                break
                        except Exception as e:
                            print(f"获取第{page}页数据失败: {str(e)}")
                            break
        
        return jsonify({"success": True, "data": 连板数据})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/max-volume', methods=['POST'])
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


@app.route('/api/next-day-jingjia', methods=['POST'])
def fetch_next_day_jingjia():
    """获取单个股票的次日竞价数据"""
    try:
        data = request.get_json()
        stock_name = data.get('stock_name')
        next_date = data.get('next_date')  # 下一交易日
        
        # 如果没有下一交易日，返回空值
        if not next_date:
            return jsonify({
                "success": True, 
                "jingjiaZhangfu": "",
                "jingjiaChengjiaoE": "",
                "jingjiaChengjiaoL": "",
                "shifoujinjie": ""
            })
        
        # 格式化日期为YYYY-MM-DD
        year = next_date[:4]
        month = next_date[4:6]
        day = next_date[6:]
        date_str = f"{year}-{month}-{day}"
        
        # 构建查询语句
        query = f"{date_str}{stock_name}涨跌且含现价且含竞价涨幅且含竞价成交额竞价成交量且含现价含涨停价"
        
        # 请求次日竞价数据
        response = requests.get(
            f"https://ai.iwencai.com/urp/v7/index/robot-index?uuid=23225&query={query}",
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
            if json_data.get("status_code") == "0":
                datas = json_data["answer"]["components"][0]["data"].get("datas", [])
                if datas:
                    first_item = datas[0]
                    
                    # 获取竞价涨幅
                    jjzf = get_field_by_keyword(first_item, "竞价涨幅")
                    jjzf_formatted = ""
                    if jjzf:
                        try:
                            jjzf_formatted = f"{float(jjzf):.2f}"
                        except:
                            jjzf_formatted = str(jjzf)
                    
                    # 获取竞价成交额
                    jjcje = get_field_by_keyword(first_item, "竞价金额")
                    jjcje_formatted = ""
                    if jjcje:
                        try:
                            jjcje_formatted = f"{float(jjcje)/100000000:.2f}"
                        except:
                            jjcje_formatted = str(jjcje)
                    
                    # 获取竞价成交量
                    jjcjl = get_field_by_keyword(first_item, "竞价量")
                    jjcjl_formatted = ""
                    if jjcjl:
                        try:
                            jjcjl_formatted = f"{int(float(jjcjl)):,}"
                        except:
                            jjcjl_formatted = str(jjcjl)
                    
                    spj = get_field_by_keyword(first_item, "收盘价:不复权")
                    zxj = get_field_by_keyword(first_item, "最新价")
                    ztj = get_field_by_keyword(first_item, "涨停价")
                    
                    # 判断是否晋级
                    sfyj = ""
                    try:
                        # 如果存在收盘价，使用收盘价判断
                        if spj and ztj:
                            # 考虑浮点数精度，使用0.01的误差范围
                            sfyj = "是" if abs(float(spj) - float(ztj)) < 0.01 else "否"
                        # 如果不存在收盘价，使用最新价判断
                        elif zxj and ztj:
                            sfyj = "是" if abs(float(zxj) - float(ztj)) < 0.01 else "否"
                        else:
                            sfyj = "未知"
                    except:
                        sfyj = "未知"
                    
                    return jsonify({
                        "success": True,
                        "jingjiaZhangfu": jjzf_formatted,
                        "jingjiaChengjiaoE": jjcje_formatted,
                        "jingjiaChengjiaoL": jjcjl_formatted,
                        "shifoujinjie": sfyj
                    })
        
        return jsonify({"success": False, "error": "未获取到数据"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def process_lianban_item(item, query_date):
    """处理单条连板数据"""
    lbs = get_field_by_keyword(item, "连续涨停天数") or get_field_by_keyword(item, "连板数")
    cje = get_field_by_keyword(item, "成交额")
    fbzj = get_field_by_keyword(item, "涨停封单额")
    spj = get_field_by_keyword(item, "收盘价")
    cjl = get_field_by_keyword(item, "成交量")
    max_1min = get_field_by_keyword(item, "最大1分钟成交量")
    zyltzb = get_field_by_keyword(item, "自由流通股")
    zyltsz = get_field_by_keyword(item, "自由流通市值")
    zshsl = get_field_by_keyword(item, "实际换手率")
    lb = get_field_by_keyword(item, "量比")
    
    # 格式化数值
    def safe_format(value, formatter):
        try:
            return formatter(value) if value else ""
        except:
            return ""
    
    return {
        "连板数": str(lbs),
        "股票代码": str(item.get("股票代码", "")),
        "股票简称": str(item.get("股票简称", "")),
        "成交额(亿元)": safe_format(cje, lambda x: f"{float(x)/100000000:.2f}"),
        "封板资金(亿元)": safe_format(fbzj, lambda x: f"{float(x)/100000000:.2f}"),
        "收盘价(元)": safe_format(spj, lambda x: f"{float(x):.2f}"),
        "成交量(股)": safe_format(cjl, lambda x: f"{int(float(x)):,}"),
        "最大1分钟成交量": "loading",
        "次日竞价涨幅(%)": "loading",
        "次日竞价成交额(亿元)": "loading",
        "次日竞价成交量": "loading",
        "自由流通股本": safe_format(zyltzb, lambda x: f"{int(float(x)):,}"),
        "自由流通市值(亿)": safe_format(zyltsz, lambda x: f"{float(x)/100000000:.2f}"),
        "真实换手率%": safe_format(zshsl, lambda x: f"{float(x):.2f}"),
        "量比": safe_format(lb, lambda x: f"{float(x):.2f}"),
        "是否晋级": "loading",
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

