"""
岗位数据导入脚本

将 Excel 文件（data/jobs.xlsx）中的岗位数据批量导入到 MySQL 数据库的 jobs 表中。
"""
import os
from typing import List, Tuple

import mysql.connector
import pandas as pd
from dotenv import load_dotenv

# 加载环境变量（数据库连接信息等）
load_dotenv()

# ---------- 数据库连接配置 ----------
# 从环境变量读取 MySQL 连接参数，提供默认值以防变量未设置
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "career_agent"),
}

# Excel 文件路径（相对于项目根目录）
EXCEL_PATH = "data/jobs.xlsx"

# 列名映射：将 Excel 中的中文列名映射为数据库表字段名
# 注意：不在映射中的列（如更新日期、岗位来源地址）将被忽略
COLUMN_MAPPING = {
    "岗位名称": "job_title",
    "地址": "location",
    "薪资范围": "salary_range",
    "公司名称": "company_name",
    "所属行业": "industry",
    "公司规模": "company_size",
    "公司类型": "company_type",
    "岗位编码": "job_code",
    "岗位详情": "job_description",
    "公司详情": "company_intro",
}


def import_jobs() -> None:
    """
    从 Excel 文件读取岗位数据并导入到 MySQL jobs 表。

    流程：
        1. 读取 Excel 文件。
        2. 根据列映射重命名列，并只保留需要的列。
        3. 将 NaN 转换为 None（用于 SQL NULL）。
        4. 建立数据库连接。
        5. 批量插入数据到 jobs 表。
        6. 提交事务，并输出成功记录数。
    """
    print("正在读取 Excel 文件...")
    # 读取 Excel 文件
    df = pd.read_excel(EXCEL_PATH)

    # 调试：打印 Excel 列名，便于确认列映射是否正确
    print("Excel 列名：", df.columns.tolist())

    # 仅保留需要导入的列，并重命名为数据库字段名
    df = df[list(COLUMN_MAPPING.keys())].rename(columns=COLUMN_MAPPING)

    # 处理空值：将 pandas 的 NaN 转换为 None，以便在 MySQL 中存储为 NULL
    df = df.where(pd.notnull(df), None)

    # 建立数据库连接
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 插入 SQL 语句，字段顺序与 DataFrame 列顺序一致
    insert_sql = """
        INSERT INTO jobs (
            job_title, location, salary_range, company_name, industry,
            company_size, company_type, job_code, job_description, company_intro
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    print("开始导入数据...")
    # 将 DataFrame 转换为元组列表（每行数据）
    data_list: List[Tuple] = [tuple(row) for row in df.to_numpy()]

    try:
        # 使用 executemany 批量插入，提高效率
        cursor.executemany(insert_sql, data_list)
        conn.commit()  # 提交事务
        print(f"成功导入 {cursor.rowcount} 条记录！")
    except Exception as e:
        print(f"导入失败：{e}")
        conn.rollback()  # 发生错误时回滚事务
    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import_jobs()