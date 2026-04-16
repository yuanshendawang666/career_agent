"""
应用配置模块

负责从环境变量和 .env 文件中加载配置，为整个应用提供统一的配置入口。
"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # MySQL 配置
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "career_agent"

    # Neo4j 配置
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    # DashScope / Qwen 配置
    dashscope_api_key: str = ""
    dashscope_base_url: str = ""
    qwen_model: str = "qwen-turbo"

    # 文件路径
    upload_dir: str = "./data/uploads"
    report_dir: str = "./data/reports"

    # JWT 配置
    secret_key: str = "change_this_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        # 环境变量前缀（可选），如果不设置，则直接匹配字段名（不区分大小写）
        # 例如 MYSQL_HOST 会映射到 mysql_host
        case_sensitive = False
        env_file = ".env"
        extra = "ignore"

settings = Settings()
print("=== Config Debug ===")
print(f"MYSQL_PASSWORD from os.getenv: {os.getenv('MYSQL_PASSWORD')}")
print(f"settings.mysql_password: {settings.mysql_password}")