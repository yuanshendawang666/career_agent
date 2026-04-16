"""
Pydantic 学生相关数据模型（Schemas）

定义学生信息的请求/响应模型。
"""
from typing import Optional, Dict, Any

from pydantic import BaseModel
from datetime import datetime

from typing import Optional, Any, List


class StudentResponse(BaseModel):
    """
    学生信息响应模型。

    用于返回学生的基本信息以及解析生成的个人画像。
    """

    id: int
    """学生唯一标识 ID"""

    name: str
    """学生姓名"""

    profile_json: Optional[Dict[str, Any]] = None
    """学生画像（JSON 格式），包含技能、能力评分、教育背景等结构化信息，可选"""

    class Config:
        from_attributes = True  # 允许从 SQLAlchemy 模型实例创建 Pydantic 对象

class ResumeVersionResponse(BaseModel):
    id: int
    version: int
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeVersionDetail(ResumeVersionResponse):
    resume_text: str
    profile_json: dict

class ManualBasicsUpdate(BaseModel):
    intended_city: Optional[str] = None
    gender: Optional[str] = None
    school: Optional[str] = None
    grade: Optional[str] = None

class ExperienceItem(BaseModel):
    name: str
    role: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None

class ExperiencesUpdate(BaseModel):
    projects: Optional[List[ExperienceItem]] = None
    papers: Optional[List[ExperienceItem]] = None
    internships: Optional[List[ExperienceItem]] = None
    competitions: Optional[List[ExperienceItem]] = None

class StudentProfileUpdateRequest(BaseModel):
    manual_basics: Optional[ManualBasicsUpdate] = None
    experiences: Optional[ExperiencesUpdate] = None
    skills: Optional[List[str]] = None
    certificates: Optional[List[str]] = None
    education: Optional[str] = None
    major: Optional[str] = None
    age: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    graduation_year: Optional[str] = None
    target_job: Optional[str] = None
    self_introduction: Optional[str] = None
    language: Optional[str] = None
    work_experience: Optional[str] = None
    internships: Optional[List[str]] = None
    innovation_score: Optional[float] = None
    innovation_reason: Optional[str] = None
    learning_score: Optional[float] = None
    learning_reason: Optional[str] = None
    stress_score: Optional[float] = None
    stress_reason: Optional[str] = None
    communication_score: Optional[float] = None
    communication_reason: Optional[str] = None
    overall_score: Optional[float] = None
    overall_reason: Optional[str] = None
    confidence_score: Optional[float] = None
    confidence_reason: Optional[str] = None
    interests: Optional[List[str]] = None
    strengths: Optional[List[str]] = None

class FreeTextParseRequest(BaseModel):
    text: str
    type: str  # "project" | "paper" | "internship" | "competition" | "basic"