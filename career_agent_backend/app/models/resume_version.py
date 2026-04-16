from sqlalchemy import Column, Integer, Text, JSON, TIMESTAMP
from sqlalchemy.sql import func
from app.database.mysql import Base

class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, nullable=False, index=True)
    version = Column(Integer, nullable=False)  # 版本号，从1开始递增
    resume_text = Column(Text)
    profile_json = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())