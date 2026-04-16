from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class PlanningProfile(Base):
    __tablename__ = "planning_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, unique=True, index=True, nullable=False)  # 关联 students.id
    interests = Column(JSON, default=[])      # 兴趣方向
    strengths = Column(JSON, default=[])      # 优势能力
    experiences = Column(JSON, default={})    # 项目/活动/竞赛经历
    self_introduction = Column(String(1000), default="")
    grade = Column(String(20), default="")    # 年级
    intended_city = Column(String(100), default="")
    gender = Column(String(10), default="")
    age = Column(String(10), default="")
    school = Column(String(100), default="")
    major = Column(String(100), default="")
    learning_plan = Column(Text, default="")  # 学习计划（持久化存储）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())