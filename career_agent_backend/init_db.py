import mysql.connector
from sqlalchemy import create_engine, text
from app.database.mysql import Base
from app.models import job, student, region_stats, user, resume_version
from app.core.config import settings

def init_database():
    # 1. 连接 MySQL 服务器（不指定数据库）
    conn = mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
    )
    cursor = conn.cursor()

    # 2. 删除旧数据库（如果存在）
    cursor.execute("DROP DATABASE IF EXISTS career_agent")
    # 3. 创建新数据库，使用 utf8mb4 编码
    cursor.execute("CREATE DATABASE career_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.close()
    conn.close()

    # 4. 连接到新数据库，创建所有表（模型定义的表）
    engine = create_engine(
        f"mysql+mysqlconnector://{settings.mysql_user}:{settings.mysql_password}@{settings.mysql_host}:{settings.mysql_port}/career_agent"
    )
    Base.metadata.create_all(bind=engine)

    # 5. 创建 jobs_computer 表（结构与 jobs 类似，并增加 is_computer 字段）
    with engine.connect() as conn:
        # 使用 text() 包装 SQL 字符串
        conn.execute(text("CREATE TABLE IF NOT EXISTS jobs_computer LIKE jobs;"))
        conn.execute(text("ALTER TABLE jobs_computer ADD COLUMN is_computer TINYINT(1) DEFAULT NULL COMMENT 'NULL=未判断, 1=是, 0=否';"))
        conn.commit()

    print("数据库 'career_agent' 及所有表创建完成！")

if __name__ == "__main__":
    init_database()