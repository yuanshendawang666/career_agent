# app/api/v1/match.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.mysql import get_db
from app.models.user import User
from app.models.student import Student
from app.schemas.report import MatchResult  # 注意：你的 MatchResult 定义在 report.py 中
from app.dependencies import get_current_user
from app.services.matching import match_student_with_all_jobs

router = APIRouter()

@router.get("/student/{student_id}", response_model=List[MatchResult])
def match_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 权限校验
    if current_user.student_id != student_id:
        raise HTTPException(status_code=404, detail="无权访问")
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 调用匹配服务（该函数返回 List[Dict]）
    results = match_student_with_all_jobs(db, student_id)
    # 转换为 Pydantic 模型列表
    return [MatchResult(**r) for r in results]