import json
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "career_agent"),
}

def create_merged_table():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 1. 删除旧表（如果存在）
        cursor.execute("DROP TABLE IF EXISTS job_full_profiles")
        print("已删除旧表 job_full_profiles（如果存在）")

        # 2. 创建新表，结构与 job_title_profiles 相同
        cursor.execute("CREATE TABLE job_full_profiles LIKE job_title_profiles")
        print("已创建表 job_full_profiles")

        # 3. 添加 region_stats 列
        cursor.execute("ALTER TABLE job_full_profiles ADD COLUMN region_stats JSON DEFAULT NULL")
        print("已添加 region_stats 列")

        # 4. 插入合并后的数据
        insert_sql = """
        INSERT INTO job_full_profiles (
            job_title, skills, certificates,
            innovation_score, innovation_reason,
            learning_score, learning_reason,
            stress_score, stress_reason,
            communication_score, communication_reason,
            internship_required,
            education_required, major_required, experience_required,
            language_required, industry_background, other_requirements,
            confidence_score, confidence_reason,
            created_at, updated_at,
            region_stats
        )
        SELECT 
            jp.job_title,
            jp.skills,
            jp.certificates,
            jp.innovation_score,
            jp.innovation_reason,
            jp.learning_score,
            jp.learning_reason,
            jp.stress_score,
            jp.stress_reason,
            jp.communication_score,
            jp.communication_reason,
            jp.internship_required,
            jp.education_required,
            jp.major_required,
            jp.experience_required,
            jp.language_required,
            jp.industry_background,
            jp.other_requirements,
            jp.confidence_score,
            jp.confidence_reason,
            jp.created_at,
            jp.updated_at,
            COALESCE(
                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'region', rs.region,
                            'demand_count', rs.demand_count,
                            'salary_min_avg', CAST(rs.salary_min_avg AS DECIMAL(10,2)),
                            'salary_max_avg', CAST(rs.salary_max_avg AS DECIMAL(10,2)),
                            'top_cities', CAST(rs.top_cities AS JSON)
                        )
                    )
                    FROM job_region_stats rs
                    WHERE rs.job_title = jp.job_title
                ),
                JSON_ARRAY()
            ) AS region_stats
        FROM job_title_profiles jp
        """
        cursor.execute(insert_sql)
        conn.commit()
        print(f"数据合并完成，共插入 {cursor.rowcount} 行记录")

        cursor.close()
        conn.close()
        print("所有操作成功完成！")

    except Error as e:
        print(f"数据库错误: {e}")

if __name__ == "__main__":
    create_merged_table()