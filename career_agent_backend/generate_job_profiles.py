"""
岗位画像生成脚本

为 jobs_computer 表中的每个岗位调用大模型生成结构化画像，
并将结果存入 job_profiles 表。
"""
import json
import logging
import os
import sys
import time
from typing import Dict, Any, Optional

import mysql.connector
from dotenv import load_dotenv
from tqdm import tqdm

# 添加项目根目录到 Python 路径（如果直接运行此脚本）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.llm_client import call_qwen

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    filename="generate_profiles.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# 可调参数
SLEEP_SECONDS = 0.2  # API 调用间隔（秒）
MAX_RETRIES = 3       # 单条最大重试次数

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "career_agent"),
    "charset": "utf8mb4",
}


def generate_profile(job_id: int, job_description: str) -> Optional[Dict[str, Any]]:
    """
    调用大语言模型为指定岗位生成画像。

    Args:
        job_id (int): 岗位 ID（用于日志）。
        job_description (str): 岗位描述文本。

    Returns:
        Optional[Dict[str, Any]]: 画像字典，包含 skills、certificates 等字段；
            若重试失败则返回 None。
    """
    system_prompt = "你是一位职业分析师，擅长从职位描述中提取结构化的岗位要求信息。"
    user_prompt = f"""
请根据以下职位描述，提取该岗位的详细画像要求。以**JSON格式**输出，包含以下字段：
- skills: 列表，具体技能名称（如["Python", "Flask"]）
- certificates: 列表，证书名称（如["CET-6", "PMP"]），若无则空列表
- innovation_score: 0-5之间的整数
- innovation_reason: 简短理由
- learning_score: 0-5整数
- learning_reason: 简短理由
- stress_score: 0-5整数
- stress_reason: 简短理由
- communication_score: 0-5整数
- communication_reason: 简短理由
- internship_required: 字符串，如"需要相关实习经验"或"无要求"
- education_required: 字符串，学历要求（如"本科及以上"），若无则空字符串
- major_required: 字符串，专业要求，若无则空字符串
- experience_required: 字符串，工作经验要求，若无则空字符串
- language_required: 字符串，语言能力要求，若无则空字符串
- industry_background: 字符串，行业背景要求，若无则空字符串
- other_requirements: 字符串，其他特殊要求，若无则空字符串

职位描述：{job_description}
"""

    for attempt in range(MAX_RETRIES):
        try:
            # 调用 LLM
            result = call_qwen(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                temperature=0.3,
            )

            # 提取 JSON（取第一个 { 和最后一个 } 之间的内容）
            start = result.find("{")
            end = result.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("返回内容中没有找到 JSON")
            json_str = result[start:end]
            data = json.loads(json_str)
            return data

        except json.JSONDecodeError as e:
            logging.warning(f"Job {job_id} attempt {attempt+1} JSON 解析失败: {e}")
        except Exception as e:
            logging.warning(f"Job {job_id} attempt {attempt+1} 失败: {e}")

        # 若还有重试机会，等待后继续
        if attempt < MAX_RETRIES - 1:
            time.sleep(2)  # 重试前等待 2 秒
        else:
            logging.error(f"Job {job_id} 最终失败，已重试 {MAX_RETRIES} 次")
            return None

    return None


def main() -> None:
    """
    主函数：从 jobs_computer 表中读取未生成画像的岗位，
    逐个调用大模型生成画像，并存入 job_profiles 表。
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    # 查询未生成画像的岗位
    cursor.execute("""
        SELECT j.id, j.job_description, j.job_title
        FROM jobs_computer j 
        LEFT JOIN job_profiles jp ON j.id = jp.job_id 
        WHERE jp.job_id IS NULL
    """)
    jobs = cursor.fetchall()
    print(f"需要生成画像的岗位数量: {len(jobs)}")

    # 可选：测试前 N 条（取消注释即可）
    # jobs = jobs[:50]

    # 插入 SQL（字段顺序与表结构一致）
    insert_sql = """
        INSERT INTO job_profiles (
            job_id, job_title, skills, certificates, 
            innovation_score, innovation_reason,
            learning_score, learning_reason,
            stress_score, stress_reason,
            communication_score, communication_reason,
            internship_required,
            education_required, major_required, experience_required,
            language_required, industry_background, other_requirements
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    success_count = 0
    for job in tqdm(jobs, desc="生成岗位画像"):
        job_id = job["id"]
        job_title = job["job_title"]
        job_desc = job["job_description"]

        # 跳过描述为空的记录
        if not job_desc or len(job_desc.strip()) == 0:
            logging.info(f"岗位 {job_id} 描述为空，跳过")
            continue

        # 调用画像生成函数
        profile = generate_profile(job_id, job_desc)
        if profile is None:
            continue

        # 准备插入数据，使用默认值填充缺失字段
        try:
            cursor.execute(
                insert_sql,
                (
                    job_id,
                    job_title,
                    json.dumps(profile.get("skills", []), ensure_ascii=False),
                    json.dumps(profile.get("certificates", []), ensure_ascii=False),
                    profile.get("innovation_score", 0),
                    profile.get("innovation_reason", ""),
                    profile.get("learning_score", 0),
                    profile.get("learning_reason", ""),
                    profile.get("stress_score", 0),
                    profile.get("stress_reason", ""),
                    profile.get("communication_score", 0),
                    profile.get("communication_reason", ""),
                    profile.get("internship_required", "无要求"),
                    profile.get("education_required", ""),
                    profile.get("major_required", ""),
                    profile.get("experience_required", ""),
                    profile.get("language_required", ""),
                    profile.get("industry_background", ""),
                    profile.get("other_requirements", ""),
                ),
            )
            conn.commit()
            success_count += 1
            logging.info(f"Job {job_id} 成功生成画像")
        except Exception as e:
            logging.error(f"Job {job_id} 数据库插入失败: {e}")
            conn.rollback()

        # 控制 API 调用频率
        time.sleep(SLEEP_SECONDS)

    print(f"处理完成！成功生成 {success_count} 个岗位画像。")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()