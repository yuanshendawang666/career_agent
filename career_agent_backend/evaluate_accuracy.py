"""
准确率评估脚本

提供以下功能：
- 随机抽样岗位画像和学生画像，供人工评估数据质量。
- 测试技能匹配函数的准确率，基于预定义的测试用例。
"""
import json
import os
import random
from typing import List, Dict, Any

import mysql.connector
from dotenv import load_dotenv

from app.utils.skill_normalizer import skill_match

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


def sample_job_profiles(n: int = 10) -> None:
    """
    从 job_title_profiles 表中随机抽样 n 条岗位画像，打印供人工评估。

    Args:
        n (int): 抽样数量，默认 10。
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT job_title, skills, education_required, confidence_score "
        "FROM job_title_profiles ORDER BY RAND() LIMIT %s",
        (n,),
    )
    rows = cursor.fetchall()

    for row in rows:
        print(f"岗位：{row['job_title']}")
        # 解析技能字段（可能是 JSON 字符串或列表）
        skills = row["skills"]
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except json.JSONDecodeError:
                skills = []
        print(f"技能：{skills}")
        print(f"学历要求：{row['education_required']}")
        print(f"置信度：{row['confidence_score']}")
        print("-" * 50)

    cursor.close()
    conn.close()


def sample_student_profiles(n: int = 10) -> None:
    """
    从 students 表中随机抽样 n 条学生画像，打印供人工评估。

    Args:
        n (int): 抽样数量，默认 10。
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT name, profile_json FROM students ORDER BY RAND() LIMIT %s", (n,)
    )
    rows = cursor.fetchall()

    for row in rows:
        print(f"学生：{row['name']}")
        # 解析 profile_json 字段（可能是 JSON 字符串或字典）
        profile = row["profile_json"]
        if isinstance(profile, str):
            try:
                profile = json.loads(profile)
            except json.JSONDecodeError:
                profile = {}
        print(f"技能：{profile.get('skills', [])}")
        print(f"学历：{profile.get('education')}")
        print(f"总体评分：{profile.get('overall_score')}")
        print(f"置信度：{profile.get('confidence_score')}")
        print(f"评分理由：{profile.get('overall_reason')}")
        print("-" * 50)

    cursor.close()
    conn.close()


def test_skill_matching() -> None:
    """
    测试技能匹配函数（skill_match）的准确率。

    使用预定义的测试用例集，计算匹配正确率，并打印失败的用例。
    """
    test_cases: List[tuple] = [
        ("python", "Python", True),
        ("python", "Py", True),
        ("java", "J2EE", True),
        ("javascript", "JS", True),
        ("react", "React.js", True),
        ("java", "c++", False),
        ("spring", "Spring Boot", False),  # 应视为不同
        ("mysql", "MySQL", True),
        ("nodejs", "node.js", True),
        ("machine learning", "ML", True),
    ]

    correct = 0
    total = len(test_cases)

    for s1, s2, expected in test_cases:
        result = skill_match(s1, s2)
        if result == expected:
            correct += 1
        else:
            print(f"失败: {s1} vs {s2} -> {result}, 期望 {expected}")

    accuracy = (correct / total) * 100
    print(f"技能匹配准确率：{accuracy:.2f}%")


if __name__ == "__main__":
    print("=== 抽样岗位画像（请人工评估准确率）===")
    sample_job_profiles(10)

    print("\n=== 抽样学生画像 ===")
    sample_student_profiles(10)

    print("\n=== 技能匹配测试 ===")
    test_skill_matching()