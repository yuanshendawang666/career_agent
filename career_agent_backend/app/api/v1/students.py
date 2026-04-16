import os
import shutil
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, attributes
from sqlalchemy.orm import Session as SQLSession

from app.database.mysql import get_db
from app.models.student import Student
from app.models.resume_version import ResumeVersion
from app.models.user import User
from app.schemas.student import (
    StudentResponse,
    StudentProfileUpdateRequest,
    ResumeVersionResponse,
    ResumeVersionDetail,
    FreeTextParseRequest
)
from app.dependencies import get_current_user
from app.core.config import settings
from app.services.resume_parser import parse_resume
from app.services.student_profile import create_student_from_resume, parse_free_text, finalize_student_profile
from app.services.student_profile import regenerate_profile_scores

router = APIRouter()

# 确保上传目录存在
os.makedirs(settings.upload_dir, exist_ok=True)


@router.post("/upload", response_model=StudentResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传简历，生成学生画像。如果用户已关联学生，则更新；否则创建新学生。"""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(400, detail="不支持的文件类型，请上传 PDF/DOCX/TXT")

    # 保存临时文件
    temp_path = os.path.join(settings.upload_dir, f"temp_{datetime.now().timestamp()}_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 解析文本
        resume_text = parse_resume(temp_path, ext)
        # 调用服务层创建或更新学生（假设该函数接收文件路径并返回 Student 对象）
        # 注意：create_student_from_resume 可能期望文件名参数，这里使用当前用户名作为临时名称
        student = create_student_from_resume(db, current_user.username, temp_path)
    except Exception as e:
        os.remove(temp_path)
        raise HTTPException(500, detail=f"处理失败: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # 关联当前用户与学生（如果尚未关联）
    if current_user.student_id != student.id:
        current_user.student_id = student.id
        db.commit()

    return StudentResponse(id=student.id, name=student.name, profile_json=student.profile_json)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.student_id != student_id:
        raise HTTPException(404, detail="无权访问")
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404, detail="学生不存在")
    return StudentResponse(id=student.id, name=student.name, profile_json=student.profile_json)


@router.put("/{student_id}/profile", response_model=StudentResponse)
def update_student_profile(
    student_id: int,
    update_data: StudentProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.student_id != student_id:
        raise HTTPException(404, detail="无权访问")
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404, detail="学生不存在")

    # 合并更新：保留原有 profile_json，更新传入的字段
    current_profile = student.profile_json or {}

    current_profile = student.profile_json or {}
    # 手动填写的基本信息
    if update_data.manual_basics:
        current_profile["manual_basics"] = update_data.manual_basics.dict(exclude_unset=True)
    if update_data.experiences:
        current_profile["experiences"] = update_data.experiences.dict(exclude_unset=True)

    # 技能与证书
    if update_data.skills is not None:
        current_profile["skills"] = update_data.skills
    if update_data.certificates is not None:
        current_profile["certificates"] = update_data.certificates

    # 教育背景
    if update_data.education is not None:
        current_profile["education"] = update_data.education
    if update_data.major is not None:
        current_profile["major"] = update_data.major

    # 基础信息
    if update_data.age is not None:
        current_profile["age"] = update_data.age
    if update_data.phone is not None:
        current_profile["phone"] = update_data.phone
    if update_data.email is not None:
        current_profile["email"] = update_data.email
    if update_data.graduation_year is not None:
        current_profile["graduation_year"] = update_data.graduation_year
    if update_data.target_job is not None:
        current_profile["target_job"] = update_data.target_job
    if update_data.self_introduction is not None:
        current_profile["self_introduction"] = update_data.self_introduction

    # 语言和工作经历（字符串）
    if update_data.language is not None:
        current_profile["language"] = update_data.language
    if update_data.work_experience is not None:
        current_profile["work_experience"] = update_data.work_experience

    # 实习经历（数组）
    if update_data.internships is not None:
        current_profile["internships"] = update_data.internships

    # 能力评分及理由
    if update_data.innovation_score is not None:
        current_profile["innovation_score"] = update_data.innovation_score
    if update_data.innovation_reason is not None:
        current_profile["innovation_reason"] = update_data.innovation_reason
    if update_data.learning_score is not None:
        current_profile["learning_score"] = update_data.learning_score
    if update_data.learning_reason is not None:
        current_profile["learning_reason"] = update_data.learning_reason
    if update_data.stress_score is not None:
        current_profile["stress_score"] = update_data.stress_score
    if update_data.stress_reason is not None:
        current_profile["stress_reason"] = update_data.stress_reason
    if update_data.communication_score is not None:
        current_profile["communication_score"] = update_data.communication_score
    if update_data.communication_reason is not None:
        current_profile["communication_reason"] = update_data.communication_reason

    # 综合评分
    if update_data.overall_score is not None:
        current_profile["overall_score"] = update_data.overall_score
    if update_data.overall_reason is not None:
        current_profile["overall_reason"] = update_data.overall_reason

    # 置信度
    if update_data.confidence_score is not None:
        current_profile["confidence_score"] = update_data.confidence_score
    if update_data.confidence_reason is not None:
        current_profile["confidence_reason"] = update_data.confidence_reason

    # 规划模式字段（兴趣、优势）
    if update_data.interests is not None:
        current_profile["interests"] = update_data.interests
    if update_data.strengths is not None:
        current_profile["strengths"] = update_data.strengths
    current_profile = regenerate_profile_scores(current_profile)
    student.profile_json = current_profile
    # 强制标记 JSON 字段已修改，确保 SQLAlchemy 检测到变化
    attributes.flag_modified(student, 'profile_json')
    db.commit()
    db.refresh(student)
    return StudentResponse(id=student.id, name=student.name, profile_json=student.profile_json)


@router.post("/{student_id}/finalize", response_model=StudentResponse)
def finalize_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """确认生成完整画像（调用大模型完善）"""
    if current_user.student_id != student_id:
        raise HTTPException(404, detail="无权访问")
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404, detail="学生不存在")

    # 调用服务层完善画像
    updated_profile = finalize_student_profile(student.profile_json)
    student.profile_json = updated_profile
    attributes.flag_modified(student, 'profile_json')
    db.commit()
    db.refresh(student)
    return StudentResponse(id=student.id, name=student.name, profile_json=student.profile_json)


@router.get("/{student_id}/versions", response_model=List[ResumeVersionResponse])
def get_resume_versions(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.student_id != student_id:
        raise HTTPException(404, detail="无权访问")
    versions = db.query(ResumeVersion).filter(ResumeVersion.student_id == student_id).order_by(ResumeVersion.version.desc()).all()
    return [
        ResumeVersionResponse(id=v.id, version=v.version, created_at=v.created_at.isoformat())
        for v in versions
    ]


@router.get("/{student_id}/versions/{version_id}", response_model=ResumeVersionDetail)
def get_resume_version(
    student_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.student_id != student_id:
        raise HTTPException(404, detail="无权访问")
    version = db.query(ResumeVersion).filter(
        ResumeVersion.id == version_id,
        ResumeVersion.student_id == student_id
    ).first()
    if not version:
        raise HTTPException(404, detail="版本不存在")
    return ResumeVersionDetail(
        id=version.id,
        version=version.version,
        created_at=version.created_at.isoformat(),
        resume_text=version.resume_text,
        profile_json=version.profile_json
    )


@router.post("/parse-text")
def parse_text(
    data: FreeTextParseRequest,
    current_user: User = Depends(get_current_user)
):
    """解析自由文本为结构化经历（调用 AI）"""
    try:
        result = parse_free_text(data.text, data.type)
        return result
    except Exception as e:
        raise HTTPException(500, detail=str(e))