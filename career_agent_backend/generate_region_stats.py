"""
区域统计数据生成脚本

根据 jobs_computer 表中的岗位招聘信息，按岗位名称和区域聚合统计，
计算各区域的需求数量、平均薪资和主要城市分布，并将结果存入 job_region_stats 表。
"""
import json
import os
import sys
from collections import defaultdict, Counter
from typing import Dict, Any

import mysql.connector
from dotenv import load_dotenv
from tqdm import tqdm

# 添加项目根目录到 Python 路径（如果直接运行此脚本）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.region import get_region_from_address
from app.utils.salary_parser import parse_salary

# 加载环境变量
load_dotenv()

# MySQL 数据库连接配置
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
}


def main() -> None:
    """
    主函数：遍历所有岗位名称，统计每个岗位在不同区域的招聘信息，
    并将聚合结果写入 job_region_stats 表。
    """
    # 连接数据库
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    # 获取所有唯一的岗位名称（从清洗后的 jobs_computer 表）
    cursor.execute("SELECT DISTINCT job_title FROM jobs_computer")
    titles = [row["job_title"] for row in cursor.fetchall()]
    print(f"共有 {len(titles)} 个岗位需要统计区域数据")

    # 清空统计表（可选，避免重复数据）
    cursor.execute("TRUNCATE TABLE job_region_stats")

    # 遍历每个岗位
    for title in tqdm(titles, desc="统计岗位区域数据"):
        # 查询该岗位的所有招聘记录
        cursor.execute(
            "SELECT location, salary_range FROM jobs_computer WHERE job_title = %s",
            (title,),
        )
        rows = cursor.fetchall()

        # 按区域聚合数据
        region_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "count": 0,
                "salaries_min": [],
                "salaries_max": [],
                "cities": Counter(),
            }
        )

        for row in rows:
            address = row["location"]
            salary_str = row["salary_range"]

            # 解析区域
            region = get_region_from_address(address)
            if region == "未知":
                continue  # 无法识别区域的记录跳过

            stats = region_stats[region]
            stats["count"] += 1

            # 提取城市（取地址第一个词，如“北京”）
            city = address.split()[0] if address else ""
            if city:
                stats["cities"][city] += 1

            # 解析薪资
            min_sal, max_sal = parse_salary(salary_str)
            if min_sal > 0:
                stats["salaries_min"].append(min_sal)
                stats["salaries_max"].append(max_sal)

        # 将聚合结果插入数据库
        for region, stats in region_stats.items():
            if stats["count"] == 0:
                continue

            # 计算平均薪资（如无薪资数据则默认为 0）
            avg_min = (
                sum(stats["salaries_min"]) / len(stats["salaries_min"])
                if stats["salaries_min"]
                else 0
            )
            avg_max = (
                sum(stats["salaries_max"]) / len(stats["salaries_max"])
                if stats["salaries_max"]
                else 0
            )

            # 取出现频率最高的 3 个城市
            top_cities = [city for city, _ in stats["cities"].most_common(3)]

            # 插入或更新统计记录
            cursor.execute(
                """
                INSERT INTO job_region_stats (job_title, region, demand_count, salary_min_avg, salary_max_avg, top_cities)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    demand_count = VALUES(demand_count),
                    salary_min_avg = VALUES(salary_min_avg),
                    salary_max_avg = VALUES(salary_max_avg),
                    top_cities = VALUES(top_cities)
                """,
                (
                    title,
                    region,
                    stats["count"],
                    avg_min,
                    avg_max,
                    json.dumps(top_cities, ensure_ascii=False),
                ),
            )
            conn.commit()  # 每个岗位的每个区域提交一次，避免长事务

    # 关闭连接
    cursor.close()
    conn.close()
    print("区域统计完成！")


if __name__ == "__main__":
    main()