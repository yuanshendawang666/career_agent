"""
SQLAlchemy ORM 岗位区域统计模型定义

用于存储不同岗位在不同地区的统计数据，如需求数量、薪资水平、主要城市分布等。
"""
from sqlalchemy import Column, Integer, String, DECIMAL, Text, TIMESTAMP
from sqlalchemy.sql import func

from app.database.mysql import Base


class JobRegionStats(Base):
    """
    岗位区域统计模型，对应数据库表 job_region_stats。

    记录某个岗位在特定地区的统计数据，包括需求数量、平均薪资、常见薪资范围及主要城市分布。
    """

    __tablename__ = "job_region_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)      # 自增主键
    job_title = Column(String(255), nullable=False)                 # 岗位名称
    region = Column(String(50), nullable=False)                     # 地区名称（如 "华东", "北京"）
    demand_count = Column(Integer)                                  # 该地区岗位需求数量
    salary_min_avg = Column(DECIMAL(10, 2))                         # 平均最低薪资（万元/年）
    salary_max_avg = Column(DECIMAL(10, 2))                         # 平均最高薪资（万元/年）
    salary_range_common = Column(String(100))                       # 常见薪资范围（如 "15k-25k"）
    top_cities = Column(Text)                                       # 主要城市分布，JSON 或逗号分隔格式
    created_at = Column(TIMESTAMP, server_default=func.now())       # 创建时间
    updated_at = Column(TIMESTAMP, onupdate=func.now())             # 更新时间