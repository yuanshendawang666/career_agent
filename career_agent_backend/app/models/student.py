"""
SQLAlchemy ORM 学生信息模型定义

用于存储学生基本信息、简历原文以及解析生成的个人画像。
"""
from sqlalchemy import Column, Integer, String, Text, JSON

from app.models.base import BaseModel


class Student(BaseModel):
    """
    学生信息模型，对应数据库表 students。

    继承自 BaseModel，自动获得 id、created_at、updated_at 字段。
    用于存储学生基本信息、简历原文以及解析生成的个人画像。
    """

    __tablename__ = "students"

    name = Column(String(100))                # 学生姓名
    resume_text = Column(Text)               # 原始简历文本（从上传文件提取的全文）
    profile_json = Column(JSON)              # 学生画像（JSON 格式），包含技能、能力评分、教育背景等结构化信息