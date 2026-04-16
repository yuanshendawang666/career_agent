from sqlalchemy import Column, Integer, String, JSON, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="student")
    studentId = Column(Integer, nullable=True)  # 关联学生表

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    profile_json = Column(JSON, nullable=True)   # 存储结构化画像
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, index=True)
    company_name = Column(String)
    location = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)

class JobTitleProfile(Base):
    __tablename__ = "job_title_profiles"

    job_title = Column(String, primary_key=True, index=True)
    skills = Column(JSON, default=list)
    certificates = Column(JSON, default=list)
    innovation_score = Column(Integer)
    innovation_reason = Column(String)
    learning_score = Column(Integer)
    learning_reason = Column(String)
    stress_score = Column(Integer)
    stress_reason = Column(String)
    communication_score = Column(Integer)
    communication_reason = Column(String)
    internship_required = Column(String)
    education_required = Column(String, nullable=True)
    major_required = Column(String, nullable=True)
    experience_required = Column(String, nullable=True)
    language_required = Column(String, nullable=True)
    industry_background = Column(String, nullable=True)
    other_requirements = Column(String, nullable=True)

class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    version = Column(Integer, nullable=False)          # 版本号
    resume_text = Column(Text, nullable=False)        # 原始文本
    profile_json = Column(JSON, nullable=False)       # 该版本的画像
    created_at = Column(DateTime(timezone=True), server_default=func.now())

