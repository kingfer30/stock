"""公共工具函数"""

def get_field_by_keyword(item_dict, keyword):
    """根据关键字匹配字段名并返回值"""
    for key in item_dict.keys():
        if keyword in key:
            return item_dict[key]
    return ""


def safe_format(value, formatter):
    """安全格式化数值"""
    try:
        return formatter(value) if value else ""
    except:
        return ""

