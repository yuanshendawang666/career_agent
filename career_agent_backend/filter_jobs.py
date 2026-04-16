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

def filter_jobs():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 创建 jobs_computer 表（如果不存在）
    cursor.execute("CREATE TABLE IF NOT EXISTS jobs_computer LIKE jobs")
    # 清空表
    cursor.execute("TRUNCATE TABLE jobs_computer")

    # 显式列出列名，避免包含 is_computer（如果已存在）
    insert_sql = """
        INSERT INTO jobs_computer (job_title, location, salary_range, company_name, industry, 
                                   company_size, company_type, job_code, job_description, company_intro)
        SELECT job_title, location, salary_range, company_name, industry, 
               company_size, company_type, job_code, job_description, company_intro
        FROM jobs
        WHERE 
            job_title IN (
                'Java', '测试工程师', '技术支持工程师', '实施工程师', '软件测试',
                'C/C++', '前端开发', '硬件测试', '销售工程师', '游戏运营',
                '质检员', '质量管理/测试', '产品经理', '项目经理/主管',
                '项目专员/助理', '项目招投标', '运营助理/专员', '网络客服'
            )
            OR job_title REGEXP '(?i)(java|python|c\\+\\+|前端|后端|开发|测试|实施|技术支持|软件|硬件|网络|数据|算法|运维|架构|产品经理|项目经理|运营)'
            OR industry REGEXP '(?i)(互联网|软件|计算机|信息技术|IT服务|科技|通信|数据|电子|人工智能)'
    """
    cursor.execute(insert_sql)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM jobs_computer")
    count = cursor.fetchone()[0]
    print(f"jobs_computer 表创建完成，共 {count} 条记录。")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    filter_jobs()