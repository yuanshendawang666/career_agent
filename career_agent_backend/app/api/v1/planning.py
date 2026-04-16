from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.planning_profile import PlanningProfile
from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import attributes
from app.models.student import Student
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base
router = APIRouter()

class SaveLearningResourceRequest(BaseModel):
    path_name: str
    content: str


class ExperienceItem(BaseModel):
    name: str
    role: Optional[str] = ""
    description: Optional[str] = ""
    technologies: Optional[List[str]] = []

class ExperiencesUpdate(BaseModel):
    projects: Optional[List[ExperienceItem]] = []
    activities: Optional[List[ExperienceItem]] = []   # 对应“活动”
    competitions: Optional[List[ExperienceItem]] = []

class PlanningProfileUpdate(BaseModel):
    interests: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    experiences: Optional[ExperiencesUpdate] = None
    self_introduction: Optional[str] = None
    grade: Optional[str] = None
    intended_city: Optional[str] = None
    # 新增
    gender: Optional[str] = None
    age: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    learning_plan: Optional[str] = None

@router.get("/profile")
def get_planning_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(PlanningProfile).filter(PlanningProfile.student_id == current_user.student_id).first()
    if not profile:
        # 返回默认空结构
        return {
            "interests": [],
            "strengths": [],
            "experiences": {"projects": [], "activities": [], "competitions": []},
            "self_introduction": "",
            "grade": "",
            "intended_city": "",
            "gender": "",
            "age": "",
            "school": "",
            "major": "",
            "learning_plan": "",
        }
    return {
        "interests": profile.interests or [],
        "strengths": profile.strengths or [],
        "experiences": profile.experiences or {"projects": [], "activities": [], "competitions": []},
        "self_introduction": profile.self_introduction or "",
        "grade": profile.grade or "",
        "intended_city": profile.intended_city or "",
        "gender": profile.gender or "",
        "age": profile.age or "",
        "school": profile.school or "",
        "major": profile.major or "",
        "learning_plan": profile.learning_plan or "",
    }

@router.put("/profile")
def update_planning_profile(
    data: PlanningProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(PlanningProfile).filter(PlanningProfile.student_id == current_user.student_id).first()
    if not profile:
        profile = PlanningProfile(student_id=current_user.student_id)
        db.add(profile)
    if data.interests is not None:
        profile.interests = data.interests
    if data.strengths is not None:
        profile.strengths = data.strengths
    if data.experiences is not None:
        profile.experiences = data.experiences.dict()
    if data.self_introduction is not None:
        profile.self_introduction = data.self_introduction
    if data.grade is not None:
        profile.grade = data.grade
    if data.intended_city is not None:
        profile.intended_city = data.intended_city
    if data.gender is not None:
        profile.gender = data.gender
    if data.age is not None:
        profile.age = data.age
    if data.school is not None:
        profile.school = data.school
    if data.major is not None:
        profile.major = data.major
    if data.learning_plan is not None:
        profile.learning_plan = data.learning_plan
    db.commit()
    return {"message": "保存成功"}


@router.post("/save-learning-resource")
def save_learning_resource(
    req: SaveLearningResourceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == current_user.student_id).first()
    if not student:
        raise HTTPException(404, detail="学生不存在")
    profile = student.profile_json or {}
    if "saved_learning_resources" not in profile:
        profile["saved_learning_resources"] = {}
    profile["saved_learning_resources"][req.path_name] = req.content
    student.profile_json = profile
    attributes.flag_modified(student, 'profile_json')
    db.commit()
    return {"message": "保存成功"}

@router.get("/get-learning-resource")
def get_learning_resource(
    path_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == current_user.student_id).first()
    if not student:
        raise HTTPException(404, detail="学生不存在")
    profile = student.profile_json or {}
    saved = profile.get("saved_learning_resources", {})
    content = saved.get(path_name, "")
    return {"content": content}