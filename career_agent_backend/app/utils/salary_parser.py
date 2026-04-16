"""
薪资解析工具模块

提供从薪资字符串中提取最低和最高薪资（单位：K/千元）的功能。
"""
import re
from typing import Tuple


def parse_salary(salary_str: str) -> Tuple[float, float]:
    """
    解析薪资格式，返回 (min_salary, max_salary)，单位为 K（千元/月）。
    支持格式：
      - "3000-4000元" → (3.0, 4.0)
      - "6000-8000元·14薪" → (6.0, 8.0)
      - "120-150元/天" → (2.61, 3.2625)  按21.75天/月
      - "7000-12000元" → (7.0, 12.0)
      - "1.2-2万" → (12.0, 20.0)
      - "5000-10000元" → (5.0, 10.0)
    """
    if not salary_str or salary_str == '面议' or salary_str == '薪资面议':
        return (0.0, 0.0)

    # 1. 处理日薪（元/天） -> 转换为月薪（21.75天）
    if '元/天' in salary_str:
        match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*元/天', salary_str)
        if match:
            min_day = float(match.group(1))
            max_day = float(match.group(2))
            min_month = min_day * 21.75
            max_month = max_day * 21.75
            return (min_month / 1000, max_month / 1000)
        match = re.search(r'(\d+(?:\.\d+)?)\s*元/天', salary_str)
        if match:
            day = float(match.group(1))
            month = day * 21.75
            val_k = month / 1000
            return (val_k, val_k)

    # 2. 处理万单位
    if '万' in salary_str:
        match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*万', salary_str)
        if match:
            min_wan = float(match.group(1))
            max_wan = float(match.group(2))
            return (min_wan * 10, max_wan * 10)   # 1万 = 10K
        match = re.search(r'(\d+(?:\.\d+)?)\s*万', salary_str)
        if match:
            val_wan = float(match.group(1))
            return (val_wan * 10, val_wan * 10)

    # 3. 处理元单位（月薪）
    # 移除 "·14薪" 等后缀
    salary_str = re.sub(r'·\d+薪', '', salary_str)
    match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*元', salary_str)
    if match:
        min_yuan = float(match.group(1))
        max_yuan = float(match.group(2))
        return (min_yuan / 1000, max_yuan / 1000)
    match = re.search(r'(\d+(?:\.\d+)?)\s*元', salary_str)
    if match:
        val_yuan = float(match.group(1))
        val_k = val_yuan / 1000
        return (val_k, val_k)

    # 4. 兼容旧格式（直接数字范围，假设单位为K）
    match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', salary_str)
    if match:
        min_val = float(match.group(1))
        max_val = float(match.group(2))
        return (min_val, max_val)

    return (0.0, 0.0)