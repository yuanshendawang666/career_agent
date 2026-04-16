from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
from typing import List, Dict, Any

from app.database.mysql import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.student import Student
from app.models.job import JobTitleProfile
from app.core.llm_client import call_qwen
from app.services.matching import match_student_with_all_jobs
from app.services.graph import get_job_paths
from app.services.report import generate_action_plan  # 复用报告服务中的 PDCA 生成函数
from sqlalchemy.orm import attributes
from app.models.planning_profile import PlanningProfile

router = APIRouter()

class PathSelectRequest(BaseModel):
    student_id: int
    path_name: str


@router.get("/recommendations")
@router.get("/recommendations")
@router.get("/recommendations")
def recommend_paths(
        student_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if student_id != current_user.student_id:
        raise HTTPException(status_code=404, detail="学生不存在或无权访问")

    # 获取规划档案
    planning = db.query(PlanningProfile).filter(PlanningProfile.student_id == student_id).first()
    if not planning:
        # 如果规划档案不存在，返回空推荐或提示
        return {"paths": []}

    # 获取所有已有典型画像的岗位名称
    job_titles = [jp.job_title for jp in db.query(JobTitleProfile.job_title).all()]
    if not job_titles:
        return {"paths": []}

    return _generate_ai_recommendation_from_planning(planning, job_titles)

def _generate_ai_recommendation_from_planning(planning: PlanningProfile, job_titles: List[str]) -> dict:
    # 从规划档案中提取数据
    interests = planning.interests or []
    strengths = planning.strengths or []
    self_introduction = planning.self_introduction or ""
    experiences = planning.experiences or {}
    projects = experiences.get("projects", [])
    activities = experiences.get("activities", [])
    competitions = experiences.get("competitions", [])
    grade = planning.grade or ""
    intended_city = planning.intended_city or ""

    # 构建经历描述
    projects_desc = "、".join([p.get("name", "") for p in projects]) if projects else "无"
    activities_desc = "、".join([a.get("name", "") for a in activities]) if activities else "无"
    competitions_desc = "、".join([c.get("name", "") for c in competitions]) if competitions else "无"

    job_list_str = "、".join(job_titles[:100])

    prompt = f"""
你是一位职业规划专家。请根据以下学生的个人档案信息（来自规划模式），从下面列出的岗位中选择 2-3 条最适合的职业发展路径。每条路径需包括名称、简介、以及当前与该路径的匹配度（0-100）。

可选岗位列表（必须从中选择）：{job_list_str}

学生档案（规划模式）：
- 年级：{grade if grade else '未提供'}
- 意向城市：{intended_city if intended_city else '未提供'}
- 兴趣方向：{', '.join(interests) if interests else '未提供'}
- 优势能力：{', '.join(strengths) if strengths else '未提供'}
- 自我介绍：{self_introduction if self_introduction else '未提供'}
- 项目经历：{projects_desc}
- 活动经历：{activities_desc}
- 竞赛经历：{competitions_desc}

请以 JSON 格式输出，格式如下：
{{
    "paths": [
        {{
            "name": "岗位名称（必须从上面列表中选择）",
            "description": "简要描述该岗位以及推荐理由",
            "match_score": 85
        }},
        ...
    ]
}}
"""
    try:
        result = call_qwen(
            user_prompt=prompt,
            system_prompt="你是一位职业规划专家。",
            max_tokens=800,
            temperature=0.5
        )
        start = result.find('{')
        end = result.rfind('}') + 1
        json_str = result[start:end]
        data = json.loads(json_str)
        valid_paths = [p for p in data.get("paths", []) if p.get("name") in job_titles]
        return {"paths": valid_paths}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐失败: {str(e)}")


def _fallback_ai_recommendation(student: Student) -> dict:
    """当匹配服务无结果时，使用 AI 生成推荐"""
    profile = student.profile_json or {}
    skills = profile.get("skills", [])
    major = profile.get("major", "")
    grade = profile.get("manual_basics", {}).get("grade", "")
    intended_city = profile.get("manual_basics", {}).get("intended_city", "")
    experiences = profile.get("experiences", {})

    prompt = f"""
你是一位职业规划专家。请根据以下学生信息，推荐2-3条适合的职业发展路径。每条路径需包括名称、简介、以及当前与该路径的匹配度（0-100）。

学生信息：
- 专业：{major}
- 年级：{grade}
- 意向城市：{intended_city}
- 技能：{', '.join(skills)}
- 项目经历：{json.dumps(experiences.get('projects', []), ensure_ascii=False)}
- 竞赛经历：{json.dumps(experiences.get('competitions', []), ensure_ascii=False)}

请以JSON格式输出，格式如下：
{{
    "paths": [
        {{
            "name": "后端开发工程师",
            "description": "负责服务器端逻辑、数据库设计、API开发等。",
            "match_score": 75
        }},
        ...
    ]
}}
"""
    try:
        result = call_qwen(
            user_prompt=prompt,
            system_prompt="你是一位职业规划专家。",
            max_tokens=800,
            temperature=0.5
        )
        start = result.find('{')
        end = result.rfind('}') + 1
        json_str = result[start:end]
        data = json.loads(json_str)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐失败: {str(e)}")


@router.post("/select")
def select_path(
    request: PathSelectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    选择路径并生成发展计划（PDCA）。
    复用报告服务中的 generate_action_plan 函数。
    """
    if request.student_id != current_user.student_id:
        raise HTTPException(status_code=404, detail="学生不存在或无权访问")
    student = db.query(Student).filter(Student.id == request.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 获取目标岗位画像
    job_profile = db.query(JobTitleProfile).filter(JobTitleProfile.job_title == request.path_name).first()
    if not job_profile:
        raise HTTPException(status_code=404, detail="目标岗位画像不存在")

    # 使用报告服务中的生成行动计划函数（基于匹配详情）
    from app.services.matching import compute_match
    match_details = compute_match(student.profile_json, job_profile)
    plan_text = generate_action_plan(student.profile_json, job_profile, match_details)

    # 可选：将选中的路径保存到学生画像中
    profile = student.profile_json or {}
    profile["selected_path"] = request.path_name
    profile["development_plan"] = plan_text
    student.profile_json = profile
    attributes.flag_modified(student, 'profile_json')  # 关键修复
    db.commit()

    return {"plan": plan_text, "message": "发展计划生成成功"}


@router.get("/refresh")
def refresh_plan(
        student_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if student_id != current_user.student_id:
        raise HTTPException(status_code=404, detail="学生不存在或无权访问")
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    profile = student.profile_json or {}
    selected_path = profile.get("selected_path")

    # 如果没有选择职业路径，返回通用建议
    if not selected_path:
        return {
            "match_score": 0,
            "advice": "请先完成兴趣探索和档案填写，系统将为你推荐合适的职业路径。",
            "alternative_path": None
        }

    # 以下为原有逻辑（保持不变）
    job_profile = db.query(JobTitleProfile).filter(JobTitleProfile.job_title == selected_path).first()
    if not job_profile:
        raise HTTPException(status_code=404, detail="目标岗位画像不存在")

    from app.services.matching import compute_match
    match_details = compute_match(student.profile_json, job_profile)
    total_score = match_details.get("total_score", 0) * 100

    skills = profile.get("skills", [])
    experiences = profile.get("experiences", {})
    prompt = f"""
请评估学生当前能力与目标岗位“{selected_path}”的匹配度，并给出具体的改进建议。如果学生经历更适合其他岗位，请推荐一个备选路径（与现有经历匹配度最高的）。

当前匹配度：{total_score:.0f}%

学生当前能力：
- 技能：{', '.join(skills)}
- 项目经历：{json.dumps(experiences.get('projects', []), ensure_ascii=False)}
- 竞赛经历：{json.dumps(experiences.get('competitions', []), ensure_ascii=False)}

输出格式：
{{
    "match_score": 70,
    "advice": "需加强...",
    "alternative_path": "数据科学"
}}
"""
    try:
        result = call_qwen(
            user_prompt=prompt,
            system_prompt="你是一位职业规划专家。",
            max_tokens=500,
            temperature=0.5
        )
        start = result.find('{')
        end = result.rfind('}') + 1
        json_str = result[start:end]
        data = json.loads(json_str)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新失败: {str(e)}")
