from pydantic import BaseModel
from typing import List, Optional

class ExperiencesUpdate(BaseModel):
    projects: Optional[List[dict]] = []
    activities: Optional[List[dict]] = []
    competitions: Optional[List[dict]] = []

class PlanningProfileUpdate(BaseModel):
    interests: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    experiences: Optional[ExperiencesUpdate] = None
    self_introduction: Optional[str] = None
    grade: Optional[str] = None
    intended_city: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    learning_plan: Optional[str] = None