from sqlalchemy import Column, Integer, String, Text, Float, JSON, DateTime
from sqlalchemy.sql import func
from app.database.mysql import Base
from app.models.base import BaseModel

class Job(BaseModel):
    __tablename__ = "jobs"

    job_title = Column(String(255))
    location = Column(String(255))
    salary_range = Column(String(100))
    company_name = Column(String(255))
    industry = Column(String(100))
    company_size = Column(String(100))
    company_type = Column(String(100))
    job_code = Column(String(100))
    job_description = Column(Text)
    company_intro = Column(Text)


class JobProfile(BaseModel):
    __tablename__ = "job_profiles"
    __table_args__ = {'extend_existing': True}   # 允许重新定义表结构

    job_id = Column(Integer, index=True)
    job_title = Column(String(255), nullable=True)
    skills = Column(JSON)
    certificates = Column(JSON)
    innovation_score = Column(Float)
    innovation_reason = Column(Text)
    learning_score = Column(Float)
    learning_reason = Column(Text)
    stress_score = Column(Float)
    stress_reason = Column(Text)
    communication_score = Column(Float)
    communication_reason = Column(Text)
    internship_required = Column(String(255))
    education_required = Column(String(255))
    major_required = Column(String(255))
    experience_required = Column(String(255))
    language_required = Column(String(255))
    industry_background = Column(String(255))
    other_requirements = Column(Text)
    confidence_score = Column(Integer, default=80)
    confidence_reason = Column(Text, default='')


class JobTitleProfile(Base):
    __tablename__ = "job_title_profiles"
    __table_args__ = {'extend_existing': True}

    job_title = Column(String(255), primary_key=True)
    skills = Column(JSON)
    certificates = Column(JSON)
    innovation_score = Column(Float)
    innovation_reason = Column(Text)
    learning_score = Column(Float)
    learning_reason = Column(Text)
    stress_score = Column(Float)
    stress_reason = Column(Text)
    communication_score = Column(Float)
    communication_reason = Column(Text)
    internship_required = Column(String(255))
    education_required = Column(String(255))
    major_required = Column(String(255))
    experience_required = Column(String(255))
    language_required = Column(String(255))
    industry_background = Column(String(255))
    other_requirements = Column(Text)
    confidence_score = Column(Integer, default=80)
    confidence_reason = Column(Text, default='')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())