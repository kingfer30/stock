"""连板数据接口"""
from flask import Blueprint, jsonify, request
import requests
import json
from utils import get_field_by_keyword, safe_format

lianban_data_bp = Blueprint('lianban_data', __name__)


def process_lianban_item(item, query_date):
    """处理单条连板数据"""
    lbs = get_field_by_keyword(item, "连续涨停天数") or get_field_by_keyword(item, "连板数")
    cje = get_field_by_keyword(item, "成交额")
    fbzj = get_field_by_keyword(item, "涨停封单额")
    spj = get_field_by_keyword(item, "收盘价")
    cjl = get_field_by_keyword(item, "成交量")
    zyltzb = get_field_by_keyword(item, "自由流通股")
    zyltsz = get_field_by_keyword(item, "自由流通市值")
    zshsl = get_field_by_keyword(item, "实际换手率")
    lb = get_field_by_keyword(item, "量比")
    
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


@lianban_data_bp.route('/api/lianban-data', methods=['POST'])
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
                    
                    while current_count < total:
                        try:
                            page_response = requests.post(
                                "https://ms.10jqka.com.cn/gateway/urp/v7/landing/getDataList",
                                data={
                                    "uuid":"23225",
                                    "comp_id":"6605812",
                                    "query_type":"stock",
                                    "query": query,
                                    "perpage":15,
                                    "page": str(page),
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
                                    page_datas = page_json["answer"]["components"][0]["data"]
                                    tm_sub = page_datas.get("datas", [])
                                    
                                    if tm_sub:
                                        for item in tm_sub:
                                            entry = process_lianban_item(item, query_date)
                                            连板数据.append(entry)
                                    
                                        current_count += len(tm_sub)
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

