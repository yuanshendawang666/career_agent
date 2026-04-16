"""
职业发展路径图构建脚本

从 MySQL 中获取所有岗位名称，调用大模型生成晋升和换岗路径，
并将这些关系存入 Neo4j 图数据库，构建完整的岗位关系图谱。
"""
import json
import os
import time
from typing import List, Dict, Optional

import mysql.connector
from dotenv import load_dotenv
from tqdm import tqdm

from app.core.llm_client import call_qwen
from app.services.graph import create_job_node, create_relationship

# 加载环境变量（数据库连接信息、API Key 等）
load_dotenv()

# MySQL 数据库连接配置（从环境变量读取）
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
}


def get_all_job_titles() -> List[str]:
    """
    从 MySQL 的 jobs 表中获取所有唯一的岗位名称。

    Returns:
        List[str]: 岗位名称列表。
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT job_title FROM jobs")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]


def generate_paths_for_job(job_title: str) -> Optional[Dict[str, List[str]]]:
    """
    调用大语言模型为给定岗位生成晋升和换岗路径。

    Args:
        job_title (str): 岗位名称。

    Returns:
        Optional[Dict[str, List[str]]]: 包含 promotions 和 transfers 两个列表的字典，
            例如 {"promotions": ["高级工程师", "技术经理"], "transfers": ["全栈开发", "架构师"]}
            若调用失败或无法解析 JSON，返回 None。
    """
    system_prompt = "你是一名职业规划专家，熟悉各行业岗位的发展路径。"
    user_prompt = f"""
请为岗位“{job_title}”列出可能的职业发展路径，包括：
1. 垂直晋升路径：该岗位在本职系内向上晋升的岗位名称（例如从“初级工程师”到“高级工程师”再到“技术经理”），最多列出3个。
2. 横向换岗路径：该岗位可以转换到的相关岗位（例如从“前端开发”可以转到“全栈开发”、“移动开发”等），最多列出3个。
**要求：必须列出至少 2 条换岗路径，最多 3 条。** 即使岗位比较专一，也请尝试找出相关的转换方向。

请以JSON格式输出，格式如下：
{{
    "promotions": ["岗位A", "岗位B", "岗位C"],
    "transfers": ["岗位X", "岗位Y", "岗位Z"]
}}
注意：只返回JSON，不要其他文字。
"""
    try:
        # 调用 LLM 接口
        result = call_qwen(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=400,
            temperature=0.2,  # 低温度使输出更稳定
        )
        # 提取 JSON 片段（取第一个 { 和最后一个 } 之间的内容）
        start = result.find("{")
        end = result.rfind("}") + 1
        if start == -1 or end == 0:
            print(f"岗位 {job_title} 返回内容中没有找到 JSON")
            return None
        json_str = result[start:end]
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError as e:
        print(f"岗位 {job_title} JSON 解析失败: {e}")
        return None
    except Exception as e:
        print(f"处理岗位 {job_title} 时出错：{e}")
        return None


def build_graph() -> None:
    """
    主函数：遍历所有岗位，生成关系并存入 Neo4j。

    流程：
        1. 获取 MySQL 中所有唯一的岗位名称。
        2. 在 Neo4j 中创建所有岗位节点（避免重复创建，提高后续关系创建效率）。
        3. 对每个岗位调用大模型获取晋升和转岗路径。
        4. 根据返回的路径创建相应的关系（PROMOTES_TO 和 TRANSFERS_TO）。
    """
    job_titles = get_all_job_titles()
    print(f"共找到 {len(job_titles)} 个唯一岗位")

    # 先创建所有岗位节点（也可在创建关系时自动创建，但先创建节点可提高性能）
    for title in tqdm(job_titles, desc="创建岗位节点"):
        create_job_node(title)

    # 为每个岗位生成路径并创建关系
    for title in tqdm(job_titles, desc="生成路径并建关系"):
        paths = generate_paths_for_job(title)
        if not paths:
            continue

        # 创建晋升关系（PROMOTES_TO）
        for target in paths.get("promotions", []):
            if target and target != title:  # 避免创建自环
                create_relationship(title, target, "PROMOTES_TO")

        # 创建转岗关系（TRANSFERS_TO）
        for target in paths.get("transfers", []):
            if target and target != title:
                create_relationship(title, target, "TRANSFERS_TO")

        # 控制请求频率，避免 API 限流
        time.sleep(0.3)

    print("图谱构建完成！")


if __name__ == "__main__":
    build_graph()