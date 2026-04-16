from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# ==================== 认证相关 ====================
class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserRegisterRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = "student"
    studentId: Optional[int] = None

class UserResponse(BaseModel):
    username: str
    role: str
    studentId: Optional[int] = None

class LoginResponse(BaseModel):
    success: bool
    user: UserResponse
    token: Optional[str] = None
    message: Optional[str] = None

# ==================== 学生相关 ====================
class StudentResponse(BaseModel):
    id: int
    name: str
    profile_json: Optional[Dict[str, Any]] = None

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

class ManualBasicsUpdate(BaseModel):
    intended_city: Optional[str] = None
    gender: Optional[str] = None
    school: Optional[str] = None
    grade: Optional[str] = None

class StudentProfileUpdateRequest(BaseModel):
    manual_basics: Optional[ManualBasicsUpdate] = None
    experiences: Optional[ExperiencesUpdate] = None
    skills: Optional[List[str]] = None
    certificates: Optional[List[str]] = None
    education: Optional[str] = None
    major: Optional[str] = None

class ResumeVersionResponse(BaseModel):
    id: int
    version: int
    created_at: str

class ResumeVersionDetail(ResumeVersionResponse):
    resume_text: str
    profile_json: Dict[str, Any]

class FreeTextParseRequest(BaseModel):
    text: str
    type: str

# ==================== 岗位相关 ====================
class JobResponse(BaseModel):
    id: int
    job_title: str
    company_name: str
    location: Optional[str] = None
    salary_range: Optional[str] = None

class RegionStatsResponse(BaseModel):
    region: str
    demand_count: int
    salary_min_avg: float
    salary_max_avg: float
    top_cities: List[str]

class JobTitleProfileResponse(BaseModel):
    job_title: str
    skills: List[str]
    certificates: List[str]
    innovation_score: float
    innovation_reason: str
    learning_score: float
    learning_reason: str
    stress_score: float
    stress_reason: str
    communication_score: float
    communication_reason: str
    internship_required: str
    education_required: Optional[str] = None
    major_required: Optional[str] = None
    experience_required: Optional[str] = None
    language_required: Optional[str] = None
    industry_background: Optional[str] = None
    other_requirements: Optional[str] = None
    region_stats: List[RegionStatsResponse] = []

# ==================== 匹配相关 ====================
class MatchResult(BaseModel):
    job_id: int
    job_title: str
    total_score: float
    details: Dict[str, float]

# ==================== 报告相关 ====================
class ReportRequest(BaseModel):
    student_id: int
    job_title: str

class ReportResponse(BaseModel):
    report_url: str
    message: str