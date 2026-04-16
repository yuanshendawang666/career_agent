"""
SQLAlchemy ORM 模型基类模块

提供所有实体模型共用的基础字段，如自增主键、创建时间和更新时间。
"""
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

from app.database.mysql import Base


class BaseModel(Base):
    """
    抽象基类模型，为所有实体模型提供通用字段。

    所有其他模型（如 Student、Job）都应继承此类，以获得：
    - 自增主键 id
    - 自动记录创建时间 created_at
    - 自动记录更新时间 updated_at

    __abstract__ = True 表示此类不会在数据库中创建对应的表，仅作为基类使用。
    """

    __abstract__ = True  # 声明为抽象类，不会映射到数据库表

    id = Column(
        Integer,
        primary_key=True,          # 设置为主键
        index=True,                # 创建索引，提升查询效率
        autoincrement=True,        # 自动递增
    )
    created_at = Column(
        DateTime(timezone=True),   # 带时区的日期时间
        server_default=func.now(), # 数据库服务器时间作为默认值，记录创建时刻
    )
    updated_at = Column(
        DateTime(timezone=True),   # 带时区的日期时间
        onupdate=func.now(),       # 更新记录时自动更新为当前时间
    )