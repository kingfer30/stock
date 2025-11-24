"""次日竞价数据接口"""
from flask import Blueprint, jsonify, request
import requests
from utils import get_field_by_keyword

next_day_jingjia_bp = Blueprint('next_day_jingjia', __name__)


@next_day_jingjia_bp.route('/api/next-day-jingjia', methods=['POST'])
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
                    if jjzf is not None and jjzf != "":
                        try:
                            jjzf_formatted = f"{float(jjzf):.2f}"
                        except:
                            jjzf_formatted = str(jjzf)
                    
                    # 获取竞价金额
                    jjcje = get_field_by_keyword(first_item, "竞价金额")
                    jjcje_formatted = ""
                    if jjcje is not None and jjcje != "":
                        try:
                            jjcje_formatted = f"{float(jjcje)/100000000:.2f}"
                        except:
                            jjcje_formatted = str(jjcje)
                    
                    # 获取竞价量
                    jjcjl = get_field_by_keyword(first_item, "竞价量")
                    jjcjl_formatted = ""
                    if jjcjl is not None and jjcjl != "":
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

