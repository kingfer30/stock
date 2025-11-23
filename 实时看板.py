import streamlit as st
import requests
import json
from datetime import datetime
import urllib3
import time

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    # "Token": "换成自己的",
    # "UserID": "换成自己的",
    "VerSion": "5.17.0.9",
    "View": "2,4,5,7,10",
    "a": "GetInfo",
    "apiv": "w38",
    "c": "Index",
}


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
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://data.10jqka.com.cn/",
            },
        )
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("status_code") == 0:
                    prev_dates = data["data"]["prev_dates"]
                    # 格式化日期为 YYYY-MM-DD 显示
                    formatted_dates = []
                    for date_str in prev_dates:
                        try:
                            formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                            formatted_dates.append({"raw": date_str, "display": formatted})
                        except:
                            formatted_dates.append({"raw": date_str, "display": date_str})
                    return formatted_dates
                else:
                    print(f"API返回错误状态: {data}")
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {str(e)}")
                print(f"响应内容: {response.text[:200]}")
        else:
            print(f"HTTP请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"获取交易日期失败: {str(e)}")
    return []


def fetch_data(selected_date=None):
    """发送POST请求并处理响应"""
    main_data = []
    竞价跌幅 = []
    竞价涨幅 = []
    连板数据 = []
    
    # 辅助函数：通过关键字匹配获取字段值
    def get_field_by_keyword(item_dict, keyword):
        """根据关键字匹配字段名并返回值"""
        for key in item_dict.keys():
            if keyword in key:
                return item_dict[key]
        return ""
    
    try:
        try:
            response = requests.post(
                BASE_URL, data=FORM_DATA, headers=HEADERS, timeout=15, verify=False
            )

            if response.status_code != 200:
                return {"error": f"接口返回异常状态码: {response.status_code}"}

            main_data = response.json()
            today = main_data.get("Day", "")
            if today == "":
                today = datetime.now().strftime("%Y-%m-%d")

            today = today.replace("-", "")

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
            if response.status_code != 200:
                return {"error": f"竞价跌幅接口返回异常状态码: {response.status_code}"}
            json_data = response.json()
            if json_data["status_code"] == "0":
                tmp = json_data["answer"]["components"][0]["data"]["datas"]
                for item in tmp:
                    # 使用模糊匹配获取字段
                    jjzf = get_field_by_keyword(item, "竞价涨幅")
                    sjzf = get_field_by_keyword(item, "最新涨跌幅")
                    if jjzf:
                        try:
                            jjzf_res = f"{float(jjzf):.2f}%"
                        except:
                            jjzf_res = str(jjzf)
                    else:
                        jjzf_res = ""
                    if sjzf:
                        try:
                            sjzf_res = f"{float(sjzf):.2f}%"
                        except:
                            sjzf_res = str(sjzf)
                    else:
                        sjzf_res = ""

                    entry = {
                        "code": str(item.get("股票代码", "")),
                        "name": str(item.get("股票简称", "")),
                        "plate": str(item.get("所属同花顺行业", "")),
                        "jjzf": jjzf_res,
                        "sjzf": sjzf_res,
                    }
                    竞价跌幅.append(entry)

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

            if response.status_code != 200:
                return {"error": f"竞价涨幅接口返回异常状态码: {response.status_code}"}
            json_data = response.json()
            if json_data["status_code"] == "0":
                tmp = json_data["answer"]["components"][0]["data"]["datas"]

                for item in tmp:
                    # 使用模糊匹配获取字段
                    jjzf = get_field_by_keyword(item, "竞价涨幅")
                    jjje = get_field_by_keyword(item, "竞价金额")
                    sjsz = get_field_by_keyword(item, "自由流通市值")
                    sjzf = get_field_by_keyword(item, "最新涨跌幅")
                    if jjzf:
                        try:
                            jjzf_res = f"{float(jjzf):.2f}%"
                        except:
                            jjzf_res = str(jjzf)
                    else:
                        jjzf_res = ""
                    if sjzf:
                        try:
                            sjzf_res = f"{float(sjzf):.2f}%"
                        except:
                            sjzf_res = str(sjzf)
                    else:
                        sjzf_res = ""

                    if jjje:
                        try:
                            jjje_res = f"{float(jjje)/100000000:.2f}亿"
                        except:
                            jjje_res = str(jjje)
                    else:
                        jjje_res = ""

                    if sjsz:
                        try:
                            sjsz_res = f"{float(sjsz)/100000000:.2f}亿"
                        except:
                            sjsz_res = str(sjsz)
                    else:
                        sjsz_res = ""
                    entry = {
                        "code": str(item.get("股票代码", "")),
                        "name": str(item.get("股票简称", "")),
                        "plate": str(item.get("所属同花顺行业", "")),
                        "jjzf": jjzf_res,
                        "sjzf": sjzf_res,
                        "jjje": jjje_res,
                        "sjsz": sjsz_res,
                    }
                    竞价涨幅.append(entry)

            # 获取连板数据
            # 构建查询语句，如果有选择日期则添加日期条件
            base_query = "连板数大于等于1且非科创板且非st股且包含成交额且包含涨停封单额且包含收盘价且包含成交量且包含最大1分钟成交量且包含次日竞价涨幅且包含次日竞价成交额且包含次日竞价成交量且包含自由流通股且包含自由流通市值且包含实际换手率且包含量比且按连续涨停天数从大到小排序"
            if selected_date:
                # 格式化日期为YYYY-MM-DD
                date_formatted = f"{selected_date[:4]}-{selected_date[4:6]}-{selected_date[6:]}"
                query = f"{date_formatted}连板数大于等于1且非科创板且非st股且包含成交额且包含涨停封单额且包含收盘价且包含成交量且包含最大1分钟成交量且包含次日竞价涨幅且包含次日竞价成交额且包含次日竞价成交量且包含自由流通股且包含自由流通市值且包含实际换手率且包含量比且按连续涨停天数从大到小排序"
            else:
                query = base_query
            
            # 定义处理单条数据的函数
            def process_lianban_item(item):
                """处理单条连板数据"""
                # 使用模糊匹配获取字段
                lbs = get_field_by_keyword(item, "连续涨停天数") or get_field_by_keyword(item, "连板数")
                cje = get_field_by_keyword(item, "成交额")
                fbzj = get_field_by_keyword(item, "涨停封单额")
                spj = get_field_by_keyword(item, "收盘价")
                cjl = get_field_by_keyword(item, "成交量")
                max_1min = get_field_by_keyword(item, "最大1分钟成交量")
                crjjzf = get_field_by_keyword(item, "次日竞价涨幅")
                crjjje = get_field_by_keyword(item, "次日竞价成交额")
                crjjcjl = get_field_by_keyword(item, "次日竞价成交量")
                zyltzb = get_field_by_keyword(item, "自由流通股")
                zyltsz = get_field_by_keyword(item, "自由流通市值")
                zshsl = get_field_by_keyword(item, "实际换手率")
                lb = get_field_by_keyword(item, "量比")
                
                # 判断是否晋级(次日竞价涨幅>0即为晋级)
                try:
                    sfyj = "是" if float(crjjzf or 0) > 0 else "否"
                except:
                    sfyj = "未知"
                
                # 格式化数值 - 添加异常处理
                try:
                    cje_formatted = f"{float(cje)/100000000:.2f}" if cje else ""
                except:
                    cje_formatted = ""
                
                try:
                    fbzj_formatted = f"{float(fbzj)/100000000:.2f}" if fbzj else ""
                except:
                    fbzj_formatted = ""
                
                try:
                    spj_formatted = f"{float(spj):.2f}" if spj else ""
                except:
                    spj_formatted = ""
                
                try:
                    cjl_formatted = f"{int(float(cjl)):,}" if cjl else ""
                except:
                    cjl_formatted = ""
                
                try:
                    max_1min_formatted = f"{int(float(max_1min)):,}" if max_1min else ""
                except:
                    max_1min_formatted = ""
                
                try:
                    crjjzf_formatted = f"{float(crjjzf):.2f}" if crjjzf else ""
                except:
                    crjjzf_formatted = ""
                
                try:
                    crjjje_formatted = f"{float(crjjje)/100000000:.2f}" if crjjje else ""
                except:
                    crjjje_formatted = ""
                
                try:
                    crjjcjl_formatted = f"{int(float(crjjcjl)):,}" if crjjcjl else ""
                except:
                    crjjcjl_formatted = ""
                
                try:
                    zyltzb_formatted = f"{int(float(zyltzb)):,}" if zyltzb else ""
                except:
                    zyltzb_formatted = ""
                
                try:
                    zyltsz_formatted = f"{float(zyltsz)/100000000:.2f}" if zyltsz else ""
                except:
                    zyltsz_formatted = ""
                
                try:
                    zshsl_formatted = f"{float(zshsl):.2f}" if zshsl else ""
                except:
                    zshsl_formatted = ""
                
                try:
                    lb_formatted = f"{float(lb):.2f}" if lb else ""
                except:
                    lb_formatted = ""
                
                return {
                    "连板数": str(lbs),
                    "股票代码": str(item.get("股票代码", "")),
                    "股票简称": str(item.get("股票简称", "")),
                    "成交额(亿元)": cje_formatted,
                    "封板资金(亿元)": fbzj_formatted,
                    "收盘价(元)": spj_formatted,
                    "成交量(股)": cjl_formatted,
                    "最大1分钟成交量": max_1min_formatted,
                    "次日竞价涨幅(%)": crjjzf_formatted,
                    "次日竞价成交额(亿元)": crjjje_formatted,
                    "次日竞价成交量": crjjcjl_formatted,
                    "自由流通股本": zyltzb_formatted,
                    "自由流通市值(亿)": zyltsz_formatted,
                    "真实换手率%": zshsl_formatted,
                    "量比": lb_formatted,
                    "是否晋级": sfyj,
                }
            
            # 第一次请求
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
            
            # 初始化：无论成功失败都清空数据，避免显示旧数据
            连板数据.clear()
            
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("status_code") == "0":
                    data_component = json_data["answer"]["components"][0]["data"]
                    tmp = data_component.get("datas", [])
                    total = data_component.get("meta", {}).get("total", 0)
                    
                    # 处理第一页数据
                    if tmp:  # 只有在有数据时才处理
                        for item in tmp:
                            entry = process_lianban_item(item)
                            连板数据.append(entry)
                    
                    # 检查是否需要分页
                    current_count = len(tmp)
                    if total > current_count:
                        # 需要获取更多页
                        page = 2
                        # 从第一次响应中获取必要的参数
                        info = data_component.get("info", {})
                        
                        while current_count < total:
                            try:
                                # 请求下一页
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
                                        if not page_datas:  # 如果没有数据了，跳出循环
                                            break
                                        
                                        # 处理本页数据
                                        for item in page_datas:
                                            entry = process_lianban_item(item)
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

            return {"success": True, "data": [main_data, 竞价涨幅, 竞价跌幅, 连板数据]}
        except json.JSONDecodeError:
            return {
                "error": "响应数据不是有效的JSON格式",
                "raw_text": response.text[:200],
            }
    except requests.exceptions.RequestException as e:
        return {"error": f"网络请求失败: {str(e)}"}
    except Exception as e:
        return {"error": f"未知错误: {str(e)}"}


def parse_response(data):
    """解析API响应数据"""
    try:
        # 调试输出原始数据结构
        st.session_state.raw_data = data
        parsed = {
            "bace_face_list": [],
            "da_ban_stats": {},
            "weather_vane": {"up": [], "down": []},
            "phb_list": [],
            "update_time": "未知",
            "day": "",
        }

        # 解析时间戳
        if "Time" in data:
            try:
                parsed["update_time"] = datetime.fromtimestamp(data["Time"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except:
                parsed["update_time"] = "时间格式错误"

        if "Day" in data:
            try:
                parsed["day"] = data["Day"]
            except:
                parsed["Day"] = ""
        # 解析BaceFaceList
        if "BaceFaceList" in data and isinstance(data["BaceFaceList"], list):
            for item in data["BaceFaceList"]:
                if len(item) >= 3:
                    parsed["bace_face_list"].append(
                        {
                            "name": str(item[0]),
                            "value": str(item[1]),
                            "id": str(item[2]),
                        }
                    )

        # 解析DaBanList
        if "DaBanList" in data and isinstance(data["DaBanList"], dict):
            # 格式化涨停破板率
            try:
                t_feng_ban = float(data["DaBanList"].get("tFengBan", "0"))
                l_feng_ban = float(data["DaBanList"].get("lFengBan", "0"))
                po_ban_rate = f"{(100 - t_feng_ban):.2f}%"
                fengban_res = f"{t_feng_ban:.2f}% / {l_feng_ban:.2f}%"
            except:
                po_ban_rate = "0.00%"

            # 格式化昨日连板今
            try:
                zr_lb_j = float(data["DaBanList"].get("ZRLBJ", "0"))
                zr_lb_j_formatted = f"{zr_lb_j:.2f}%"
            except:
                zr_lb_j_formatted = "0.00%"

            parsed["da_ban_stats"] = {
                "zhangting": f"{data["DaBanList"].get("tZhangTing", "0")} / {data["DaBanList"].get("lZhangTing", "0")}",
                "fengban": fengban_res,
                "dieting": f"{data["DaBanList"].get("tDieTing", "0")} / {data["DaBanList"].get("lDieTing", "0")}",
                "zhangdie": f"{data["DaBanList"].get("SZJS", "0")} / {data["DaBanList"].get("PPJS", "0")} / {data["DaBanList"].get("XDJS", "0")}",
                "heat_index": data["DaBanList"].get("ZHQD", "0"),
                "涨停破板率": po_ban_rate,
                "昨日涨停今": data["DaBanList"].get("ZRZTJ", "0"),
                "昨日连板今": zr_lb_j_formatted,
                "上证量能": data["DaBanList"].get("szln", "0"),
                "沪深量能": data["DaBanList"].get("qscln", "0"),
                "上证昨日量能": data["DaBanList"].get(
                    "s_zrcs", "0"
                ),  # s_zrcs和s_zrtj相同值
                "沪深昨日量能": data["DaBanList"].get(
                    "q_zrcs", "0"
                ),  # q_zrcs和q_zrtj相同值
            }


        # 解析排行榜
        if "PHBList" in data and isinstance(data["PHBList"], list):
            for item in data["PHBList"]:
                if len(item) >= 6:
                    parsed["phb_list"].append(
                        {
                            "code": str(item[0]),
                            "name": str(item[1]),
                            "change": (
                                f"{float(item[2]):.2f}%"
                                if isinstance(item[2], (int, float))
                                else str(item[2])
                            ),
                            "days": str(item[3]),
                            "type": str(item[4]),
                            "concept": str(item[5]),
                        }
                    )

        return parsed

    except Exception as e:
        st.error(f"数据解析失败: {str(e)}")
        st.write("解析失败时的数据片段:", json.dumps(data, ensure_ascii=False)[:300])
        return None


def main():
    st.set_page_config(
        page_title="股市实时监控看板", layout="wide", initial_sidebar_state="expanded"
    )

    # 自动刷新控制
    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = True
    
    # 初始化交易日期
    if "trade_dates" not in st.session_state:
        st.session_state.trade_dates = []
    
    # 初始化选择的日期
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = None
    
    # 获取数据
    with st.spinner("正在获取最新数据..."):
        result = fetch_data(st.session_state.selected_date)

    if "error" in result:
        st.error(result["error"])
        if "raw_text" in result:
            st.write("原始响应内容:", result["raw_text"])
        st.markdown(
            """
        **请检查：**
        1. 网络连接是否正常
        2. 是否使用了VPN/代理
        3. 尝试刷新页面
        4. 如果持续失败，可能是接口不可用
        """
        )
        return

    st.toast("数据获取成功！")
    raw_data = result["data"]  # 这是包含四个元素的数组

    # 分离四个数据源
    main_data = raw_data[0]  # 主要市场数据
    竞价涨幅 = raw_data[1]  # 竞价涨幅数据
    竞价跌幅 = raw_data[2]  # 竞价跌幅数据
    连板数据 = raw_data[3] if len(raw_data) > 3 else []  # 连板数据

    # 解析主要数据
    data = parse_response(main_data)
   

    if not data:
        st.error("数据解析失败，原始数据结构：")
        st.json(main_data)
        return

    print(data['update_time'])

    # 显示基础信息和自动刷新控制在同一行
    col1, col2, col3 = st.columns([3, 1, 2])
    with col1:
        st.subheader(f"📈 股市实时监控看板【 {data['day']}】 更新于@ {data['update_time']}")
    
    with col2:
        auto_refresh = st.checkbox("自动刷新", value=st.session_state.auto_refresh)
        st.session_state.auto_refresh = auto_refresh
    
    st.markdown("---")

    # 关键指标卡片
    cols = st.columns(6)
    metrics = [
        ("今涨停/昨涨停", data["da_ban_stats"]["zhangting"], "#F44336"),
        ("今跌停/昨跌停", data["da_ban_stats"]["dieting"], "#4CAF50"),
        ("今封板/昨封板", f"{data['da_ban_stats']['fengban']}", "#2196F3"),
        (
            "炸板率/连板率",
            f"{data['da_ban_stats']['涨停破板率']} / {data['da_ban_stats']['昨日连板今']}",
            "#2196F3",
        ),
        ("上涨/平盘/下跌", data["da_ban_stats"]["zhangdie"], "#FF9800"),
        ("市场热度", data["da_ban_stats"]["heat_index"], "#FF00D4"),
    ]

    for col, (title, value, color) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
            <div style='
                padding: 20px;
                background: {color}10;
                border-radius: 10px;
                border-left: 5px solid {color};
                margin: 10px 0;
            '>
                <span style='color: {color}; margin:0;font-size:2rem;font-weight:bold;'>{title}</span>
                <br/>
                <span style='color: {color}; margin:0;font-size:1.5rem;'>{value}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # 数据表格展示
    tab1, tab2, tab3, tab4 = st.tabs(["📈 竞价涨幅(一进二)", "📉 竞价跌幅", "🏆 连板排行", "🔥 连板数据"])

    with tab1:
        if 竞价涨幅:
            st.dataframe(
                竞价涨幅,
                column_config={
                    "code": "代码",
                    "name": "名称",
                    "plate": "板块",
                    "jjzf": "竞价涨幅",
                    "sjzf": "实际涨幅",
                    "jjje": "竞价金额",
                    "sjsz": "实际市值",
                },
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("暂无领涨数据")

    with tab2:
        if 竞价跌幅:
            st.dataframe(
                竞价跌幅,
                column_config={
                    "code": "代码",
                    "name": "名称",
                    "plate": "板块",
                    "jjzf": "竞价涨幅",
                    "sjzf": "实际涨幅",
                },
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("暂无领跌数据")

    with tab3:
        if data["phb_list"]:
            st.dataframe(
                data["phb_list"],
                column_config={
                    "code": "代码",
                    "name": "名称",
                    "change": "涨幅",
                    "days": "天数",
                    "type": "类型",
                    "concept": "概念",
                },
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("当前无连板数据")

    with tab4:
        #获取交易日期列表（如果还没有获取）
        if not st.session_state.trade_dates:
            st.session_state.trade_dates = get_trade_dates()
            if not st.session_state.trade_dates:
                st.warning("⚠️ 无法获取历史交易日期列表，仅显示当前交易日数据")
                
        
        # 添加日期选择下拉框 - 始终显示
        date_options = ["当前交易日"]
        if st.session_state.trade_dates:
            date_options += [d["display"] for d in st.session_state.trade_dates]
        
        [col_date1]= st.columns([2])
        with col_date1:
            selected_display = st.selectbox(
                "📅 选择查询日期",
                options=date_options,
                index=0,
                key="date_selector"
            )
    
        
        # 根据选择更新session_state
        new_selected_date = None
        if selected_display == "当前交易日":
            new_selected_date = None
        else:
            # 找到对应的原始日期
            for d in st.session_state.trade_dates:
                if d["display"] == selected_display:
                    new_selected_date = d["raw"]
                    break
        
        # 如果日期改变，重新加载页面
        if new_selected_date != st.session_state.selected_date:
            st.session_state.selected_date = new_selected_date
            st.rerun()
        
        # 添加分隔线
        st.markdown("---")
        
        # 显示数据
        data_container = st.container()
        with data_container:
            if 连板数据 and len(连板数据) > 0:
                st.dataframe(
                    连板数据,
                    column_config={
                        "连板数": "连板数",
                        "股票代码": "代码",
                        "股票简称": "名称",
                        "成交额(亿元)": "成交额(亿元)",
                        "封板资金(亿元)": "封板资金(亿元)",
                        "收盘价(元)": "收盘价(元)",
                        "成交量(股)": "成交量(股)",
                        "最大1分钟成交量": "最大1分钟成交量",
                        "次日竞价涨幅(%)": "次日竞价涨幅(%)",
                        "次日竞价成交额(亿元)": "次日竞价成交额(亿元)",
                        "次日竞价成交量": "次日竞价成交量",
                        "自由流通股本": "自由流通股本",
                        "自由流通市值(亿)": "自由流通市值(亿)",
                        "真实换手率%": "真实换手率%",
                        "量比": "量比",
                        "是否晋级": "是否晋级",
                    },
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.markdown("""
            <div style="padding: 2rem; text-align: center; background-color: #fff3cd; border-radius: 0.5rem; border: 1px solid #ffeeba;">
                <h4 style="color: #856404;">⚠️ 暂无连板数据</h4>
                <p style="color: #856404;">该日期可能没有符合条件的股票</p>
                <p style="color: #856404;">💡 提示：请尝试选择其他交易日期或等待市场开盘后查看数据</p>
            </div>
            """, unsafe_allow_html=True)

    # 热门概念展示
    with st.expander("🔥 热门概念", expanded=True):
        if data["bace_face_list"]:
            for item in data["bace_face_list"]:
                try:
                    value = float(item["value"].replace("%", ""))
                except:
                    value = 0

                st.markdown(
                    f"""
                <div style='
                    margin: 10px 0;
                    padding: 10px;
                    border-radius: 8px;
                '>
                    <div style='
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 5px;
                    '>
                        <span>{item['name']}</span>
                        <span>{item['value']}</span>
                    </div>
                    <div style='
                        height: 20px;
                        background: #e0e0e0;
                        border-radius: 10px;
                        overflow: hidden;
                    '>
                        <div style='
                            width: {value}%;
                            height: 100%;
                            background: linear-gradient(90deg, #2196F3, #03A9F4);
                            transition: width 0.5s ease;
                        '></div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning("暂无热门概念数据")
            
    with col3:
        if st.session_state.auto_refresh:
            # 显示倒计时
            placeholder = st.empty()
            for i in range(5, 0, -1):  # 5秒倒计时
                placeholder.text(f"🔄 自动刷新中... {i}秒后更新")
                time.sleep(1)
            st.rerun()

if __name__ == "__main__":
    main()
