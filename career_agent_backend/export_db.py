import json
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Laijingxuan2758",
    "database": "career_agent",
}

def export_all_tables():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    # 获取所有表名
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()

    # 为每张表生成 JSON 文件
    for table in tables:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            with open(f"{table}.json", "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=2, default=str)
            print(f"Exported {table}: {len(rows)} rows")
            cursor.close()
        except Exception as e:
            print(f"Failed to export {table}: {e}")
    conn.close()

if __name__ == "__main__":
    export_all_tables()