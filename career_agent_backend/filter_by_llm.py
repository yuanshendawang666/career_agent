import json
import time
import mysql.connector
from dotenv import load_dotenv
import os
from tqdm import tqdm
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.llm_client import call_qwen

load_dotenv()

db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT')),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4'
}


def classify_job_description(job_id: int, job_title: str, description: str) -> bool:
    """调用大模型判断岗位是否属于计算机/信息技术领域"""
    if not description or len(description.strip()) < 10:
        # 如果描述太短，仅根据标题简单判断（可选逻辑，防止误删）
        if job_title and any(kw in job_title for kw in ["开发", "工程师", "程序", "运维", "测试", "IT"]):
            return True
        return False

    system_prompt = "你是一个专业的IT招聘助手。请根据岗位信息判断是否属于互联网/IT/计算机/电子/通信相关领域。"

    # 优化后的Prompt：更宽松，明确保留技术支持、实施、硬件等岗位
    user_prompt = f"""
请判断以下岗位是否属于【互联网/IT/计算机/电子/通信】相关领域。

判定为"是"的标准（满足以下任一条件即可）：
1. 研发类：软件开发、前端、后端、移动端、游戏开发、算法、大数据、人工智能等。
2. 技术类：测试、运维、DBA、网络安全、技术支持、实施工程师、IT运维。
3. 硬件类：嵌入式、物联网、硬件工程师、通信工程师、电子工程师。
4. 管理类：技术经理、技术总监、IT项目经理、技术合伙人。
5. 交叉类：需要编程技能或计算机专业知识的产品经理、数据分析岗位。

判定为"否"的标准：
纯销售（如销售代表）、纯行政/人事/财务/法务、普通司机/保洁/保安、非技术类的普工/技工。

岗位名称：{job_title}
岗位详情：{description[:1000]}

请严格按要求判断，输出JSON格式：{{"is_computer": true}} 或 {{"is_computer": false}}。
只输出JSON，不要其他文字。
"""
    try:
        result = call_qwen(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=100,
            temperature=0.1
        )
        # 提取JSON
        start = result.find('{')
        end = result.rfind('}') + 1
        json_str = result[start:end]
        data = json.loads(json_str)
        return data.get('is_computer', False)
    except Exception as e:
        print(f"Job {job_id} 判断失败: {e}")
        return False


def main():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # 1. 获取所有未判断的岗位（同时获取 job_title）
    cursor.execute("SELECT id, job_title, job_description FROM jobs_computer WHERE is_computer IS NULL")
    jobs = cursor.fetchall()
    print(f"需要判断的岗位数量: {len(jobs)}")

    # 注意：如果只是测试，请保留下面这行；如果正式运行，请注释掉
    # jobs = jobs[:50]

    for job in tqdm(jobs, desc="判断岗位是否计算机相关"):
        job_id = job['id']
        job_title = job['job_title']  # 新增获取标题
        description = job['job_description']

        # 传入 job_title
        is_computer = classify_job_description(job_id, job_title, description)

        # 更新标志
        cursor.execute(
            "UPDATE jobs_computer SET is_computer = %s WHERE id = %s",
            (1 if is_computer else 0, job_id)
        )
        conn.commit()
        time.sleep(0.2)  # 避免API限流

    # 2. 删除非计算机相关的记录
    cursor.execute("DELETE FROM jobs_computer WHERE is_computer = 0")
    conn.commit()
    print(f"筛选完成，删除了非计算机岗位记录数共: {cursor.rowcount}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()