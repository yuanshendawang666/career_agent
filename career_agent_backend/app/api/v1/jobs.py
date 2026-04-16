from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.mysql import get_db
from app.models.job import Job, JobTitleProfile
from app.models.region_stats import JobRegionStats
from app.schemas.job import JobResponse, JobTitleProfileResponse, RegionStatsResponse
from urllib.parse import unquote

router = APIRouter()

@router.get("/", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    """获取所有已有典型画像的岗位基本信息（从 job_title_profiles 表）"""
    profiles = db.query(JobTitleProfile).all()
    # 构造 JobResponse 列表，id 使用自增序号，其他字段留空
    jobs = [
        JobResponse(
            id=idx + 1,
            job_title=profile.job_title,
            company_name="",      # 无公司信息
            location="",          # 无地点信息
            salary_range=""       # 无薪资信息
        )
        for idx, profile in enumerate(profiles)
    ]
    return jobs


@router.get("/{job_title}/profile", response_model=JobTitleProfileResponse)
def get_job_profile(job_title: str, db: Session = Depends(get_db)):
    job_title = job_title.replace('%2F', '/')
    job_title = unquote(job_title)
    """获取岗位的典型画像（含区域统计）"""
    # 精确匹配
    profile = db.query(JobTitleProfile).filter(JobTitleProfile.job_title == job_title).first()
    # 模糊匹配（可选）
    if not profile:
        profile = db.query(JobTitleProfile).filter(JobTitleProfile.job_title.like(f"%{job_title}%")).first()
    if not profile:
        raise HTTPException(status_code=404, detail="岗位画像不存在")

    # 使用匹配到的实际岗位名称查询区域统计
    region_stats = db.query(JobRegionStats).filter(JobRegionStats.job_title == profile.job_title).all()
    region_stats_resp = []
    for stat in region_stats:
        import json
        top_cities = []
        if stat.top_cities:
            try:
                top_cities = json.loads(stat.top_cities)
            except:
                top_cities = []
        region_stats_resp.append(
            RegionStatsResponse(
                region=stat.region,
                demand_count=stat.demand_count,
                salary_min_avg=float(stat.salary_min_avg) if stat.salary_min_avg else 0,
                salary_max_avg=float(stat.salary_max_avg) if stat.salary_max_avg else 0,
                top_cities=top_cities,
            )
        )

    return JobTitleProfileResponse(
        job_title=profile.job_title,
        skills=profile.skills,
        certificates=profile.certificates,
        innovation_score=profile.innovation_score,
        innovation_reason=profile.innovation_reason,
        learning_score=profile.learning_score,
        learning_reason=profile.learning_reason,
        stress_score=profile.stress_score,
        stress_reason=profile.stress_reason,
        communication_score=profile.communication_score,
        communication_reason=profile.communication_reason,
        internship_required=profile.internship_required,
        education_required=profile.education_required,
        major_required=profile.major_required,
        experience_required=profile.experience_required,
        language_required=profile.language_required,
        industry_background=profile.industry_background,
        other_requirements=profile.other_requirements,
        region_stats=region_stats_resp,
    )

# ================== 岗位名称列表接口 ==================
@router.get("/job-titles", response_model=List[str])
def get_job_titles(db: Session = Depends(get_db)):
    """获取去重后的岗位名称列表（用于前端搜索/下拉）"""
    titles = db.query(JobTitleProfile.job_title).distinct().all()
    return [title[0] for title in titles]