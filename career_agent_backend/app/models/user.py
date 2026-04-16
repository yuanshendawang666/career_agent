from sqlalchemy import Column, Integer, String
from app.database.mysql import Base
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # 哈希后的密码
    role = Column(String(20), default='student')
    student_id = Column(Integer, nullable=True, unique=True)  # 关联学生表，一个用户对应一个学生
    email = Column(String(100), unique=True, nullable=True)