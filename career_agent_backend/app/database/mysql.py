"""
MySQL 数据库连接模块

负责创建 SQLAlchemy 数据库引擎、会话工厂和 ORM 基类。
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 构建 MySQL 连接 URL，使用 mysql-connector-python 驱动
# 格式：mysql+mysqlconnector://用户名:密码@主机:端口/数据库名
SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqlconnector://{settings.mysql_user}:{settings.mysql_password}"
    f"@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"
)

# 创建数据库引擎
# 负责管理连接池，是 SQLAlchemy 与数据库交互的入口
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建会话工厂
# SessionLocal 是一个线程安全的会话类，用于生成数据库会话（Session）对象
# autocommit=False：不自动提交，需手动调用 commit()
# autoflush=False：不自动刷新，避免不必要的查询
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 ORM 模型的基类
# 所有模型类（如 Student、Job）都需要继承此 Base，以便 SQLAlchemy 能够正确映射表结构
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()