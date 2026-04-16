import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'career_agent'),
    'charset': 'utf8mb4'
}

print("正在连接数据库：", db_config['database'])

# 临时测试连接，查看当前数据库中的表
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print("当前数据库中的表：", [t[0] for t in tables])

# 查看 job_profiles 表结构
cursor.execute("DESCRIBE job_profiles")
cols = cursor.fetchall()
print("job_profiles 表字段：", [col[0] for col in cols])

cursor.close()
conn.close()
















"""
岗位画像聚合脚本

从 job_profiles 表中读取每个岗位的所有个体画像，按岗位名称聚合生成典型画像，
并将结果写入 job_title_profiles 表。用于生成岗位名称级别的统一画像。
"""
import json
import os
from collections import Counter
from typing import List, Dict, Any, Optional

import mysql.connector
from dotenv import load_dotenv
from tqdm import tqdm

# 加载环境变量
load_dotenv()

# 数据库连接配置
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "career_agent"),
    "charset": "utf8mb4",
}


def safe_json_loads(val: Any) -> List:
    """
    安全地将 JSON 字符串或列表解析为 Python 列表。

    Args:
        val (Any): 输入值，可以是列表、JSON 字符串或其他类型。

    Returns:
        List: 解析后的列表，解析失败或输入无效时返回空列表。
    """
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            return []
    return []


def aggregate_profiles() -> None:
    """
    聚合所有岗位的个体画像，生成岗位名称级别的典型画像。

    流程：
        1. 从 job_profiles 表中获取所有唯一的岗位名称。
        2. 对每个岗位名称，收集其所有个体画像记录。
        3. 聚合技能、证书、能力评分、招聘要求等字段（取众数或平均值）。
        4. 将聚合结果插入或更新到 job_title_profiles 表中（先清空表）。
    """
    # 连接数据库
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    # 获取所有唯一的岗位名称
    cursor.execute("SELECT DISTINCT job_title FROM job_profiles")
    titles = [row["job_title"] for row in cursor.fetchall()]
    print(f"共有 {len(titles)} 个唯一岗位名称")

    # 清空目标表，准备重新插入
    cursor.execute("TRUNCATE TABLE job_title_profiles")

    # 插入 SQL 语句（字段顺序与表结构一致）
    insert_sql = """
        INSERT INTO job_title_profiles (
            job_title, skills, certificates,
            innovation_score, innovation_reason,
            learning_score, learning_reason,
            stress_score, stress_reason,
            communication_score, communication_reason,
            internship_required,
            education_required, major_required, experience_required,
            language_required, industry_background, other_requirements,
            confidence_score, confidence_reason
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # 遍历每个岗位名称，进行聚合
    for title in tqdm(titles, desc="聚合岗位画像"):
        # 查询该岗位的所有个体画像
        cursor.execute(
            """
            SELECT skills, certificates,
                   innovation_score, innovation_reason,
                   learning_score, learning_reason,
                   stress_score, stress_reason,
                   communication_score, communication_reason,
                   internship_required,
                   education_required, major_required, experience_required,
                   language_required, industry_background, other_requirements,
                   confidence_score, confidence_reason
            FROM job_profiles
            WHERE job_title = %s
            """,
            (title,),
        )
        rows = cursor.fetchall()
        if not rows:
            continue

        # 技能聚合：统计所有技能出现频率，保留出现率 ≥30% 的技能，最多 10 个
        all_skills = []
        for row in rows:
            skills = safe_json_loads(row["skills"])
            all_skills.extend(skills)
        skill_counter = Counter(all_skills)
        total_count = len(rows)
        common_skills = [
            skill
            for skill, cnt in skill_counter.items()
            if cnt / total_count >= 0.3
        ]
        if len(common_skills) > 10:
            common_skills = [skill for skill, _ in skill_counter.most_common(10)]

        # 证书聚合：保留出现率 ≥30% 的证书，最多 5 个
        all_certs = []
        for row in rows:
            certs = safe_json_loads(row["certificates"])
            all_certs.extend(certs)
        cert_counter = Counter(all_certs)
        common_certs = [
            cert
            for cert, cnt in cert_counter.items()
            if cnt / total_count >= 0.3
        ]
        common_certs = common_certs[:5]

        # 能力评分：取平均值
        def avg_score(field: str) -> float:
            values = [row[field] for row in rows if row[field] is not None]
            return sum(values) / len(values) if values else 0.0

        innovation_score = avg_score("innovation_score")
        learning_score = avg_score("learning_score")
        stress_score = avg_score("stress_score")
        communication_score = avg_score("communication_score")

        # 理由字段：取出现次数最多的理由（众数）
        def most_common_reason(field: str) -> str:
            reasons = [
                row[field]
                for row in rows
                if row[field] and row[field].strip()
            ]
            if not reasons:
                return ""
            counter = Counter(reasons)
            return counter.most_common(1)[0][0]

        innovation_reason = most_common_reason("innovation_reason")
        learning_reason = most_common_reason("learning_reason")
        stress_reason = most_common_reason("stress_reason")
        communication_reason = most_common_reason("communication_reason")

        # 实习要求：取众数
        internship_counts = Counter(
            row["internship_required"] for row in rows if row["internship_required"]
        )
        internship_required = (
            internship_counts.most_common(1)[0][0] if internship_counts else "无要求"
        )

        # 学历要求：取众数
        edu_counts = Counter(
            row["education_required"] for row in rows if row["education_required"]
        )
        education_required = edu_counts.most_common(1)[0][0] if edu_counts else ""

        # 专业要求：取众数
        major_counts = Counter(
            row["major_required"] for row in rows if row["major_required"]
        )
        major_required = major_counts.most_common(1)[0][0] if major_counts else ""

        # 工作经验要求：取众数
        exp_counts = Counter(
            row["experience_required"] for row in rows if row["experience_required"]
        )
        experience_required = exp_counts.most_common(1)[0][0] if exp_counts else ""

        # 语言要求：取众数
        lang_counts = Counter(
            row["language_required"] for row in rows if row["language_required"]
        )
        language_required = lang_counts.most_common(1)[0][0] if lang_counts else ""

        # 行业背景：取众数
        ind_counts = Counter(
            row["industry_background"] for row in rows if row["industry_background"]
        )
        industry_background = ind_counts.most_common(1)[0][0] if ind_counts else ""

        # 其他要求：取众数
        other_counts = Counter(
            row["other_requirements"] for row in rows if row["other_requirements"]
        )
        other_requirements = other_counts.most_common(1)[0][0] if other_counts else ""

        # 置信度：取平均值
        confidence_scores = [
            row.get("confidence_score", 80) for row in rows if row.get("confidence_score")
        ]
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores) if confidence_scores else 80
        )
        confidence_reason = (
            f"基于 {len(confidence_scores)} 条招聘信息综合统计，平均置信度 {avg_confidence:.0f} 分。"
        )

        # 插入聚合结果
        cursor.execute(
            insert_sql,
            (
                title,
                json.dumps(common_skills, ensure_ascii=False),
                json.dumps(common_certs, ensure_ascii=False),
                innovation_score,
                innovation_reason,
                learning_score,
                learning_reason,
                stress_score,
                stress_reason,
                communication_score,
                communication_reason,
                internship_required,
                education_required,
                major_required,
                experience_required,
                language_required,
                industry_background,
                other_requirements,
                avg_confidence,
                confidence_reason,
            ),
        )
        conn.commit()  # 每处理一个岗位提交一次，避免长事务

    # 关闭数据库连接
    cursor.close()
    conn.close()
    print("聚合完成！")


if __name__ == "__main__":
    aggregate_profiles()