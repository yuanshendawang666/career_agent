"""
人岗匹配计算服务模块

提供学生与岗位的匹配度计算功能，包括基础要求、职业技能、职业素养和发展潜力四个维度的评估。
"""
import json
import re
from typing import Dict, Any, List, Optional, Union

from sqlalchemy.orm import Session

from app.models.job import JobTitleProfile
from app.models.student import Student
from app.utils.skill_normalizer import skill_match
from app.models.job import Job


def compute_base_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """
    计算基础要求匹配度（学历、专业、工作经验、语言、实习）。

    Args:
        student (Dict[str, Any]): 学生画像字典。
        job (JobTitleProfile): 岗位画像对象。

    Returns:
        float: 基础匹配得分，范围 0~1。
    """
    # 学历匹配
    edu_match = 1.0
    if job.education_required and student.get("education"):
        job_edu = job.education_required.lower()
        stu_edu = student["education"].lower()
        if "本科" in job_edu and stu_edu not in ["本科", "硕士"]:
            edu_match = 0.0
        elif "硕士" in job_edu and stu_edu != "硕士":
            edu_match = 0.0

    # 专业匹配（简单关键词包含）
    major_match = 1.0
    if job.major_required and student.get("major"):
        if job.major_required.lower() not in student["major"].lower():
            major_match = 0.5

    # 工作经验匹配（提取年限）
    exp_match = 1.0
    if job.experience_required and student.get("work_experience"):
        job_year = 0
        match = re.search(r"\d+", job.experience_required)
        if match:
            job_year = int(match.group())
        stu_year = 0
        match = re.search(r"\d+", student["work_experience"])
        if match:
            stu_year = int(match.group())
        if stu_year < job_year:
            exp_match = 0.0

    # 语言匹配
    lang_match = 1.0
    if job.language_required and student.get("language"):
        if job.language_required.lower() not in student["language"].lower():
            lang_match = 0.0

    # 实习要求匹配
    intern_match = 1.0
    if job.internship_required and "需要" in job.internship_required:
        if not student.get("internships"):
            intern_match = 0.0

    return (edu_match + major_match + exp_match + lang_match + intern_match) / 5


def compute_professional_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """
    计算职业技能匹配度（技能、证书）。

    Args:
        student (Dict[str, Any]): 学生画像字典。
        job (JobTitleProfile): 岗位画像对象。

    Returns:
        float: 职业技能匹配得分，范围 0~1。
    """
    # 技能匹配（使用模糊匹配）
    student_skills = set(student.get("skills", []))
    job_skills_raw = job.skills
    if isinstance(job_skills_raw, str):
        job_skills = set(json.loads(job_skills_raw))
    else:
        job_skills = set(job_skills_raw)

    matched = 0
    for js in job_skills:
        if any(skill_match(js, ss) for ss in student_skills):
            matched += 1
    skill_match_rate = matched / len(job_skills) if job_skills else 1.0

    # 证书匹配
    student_certs = set(student.get("certificates", []))
    job_certs_raw = job.certificates
    if isinstance(job_certs_raw, str):
        job_certs = set(json.loads(job_certs_raw))
    else:
        job_certs = set(job_certs_raw)

    cert_match = len(student_certs & job_certs) / len(job_certs) if job_certs else 1.0

    return (skill_match_rate + cert_match) / 2


def compute_quality_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """
    计算职业素养匹配度（创新、学习、抗压、沟通能力）。

    Args:
        student (Dict[str, Any]): 学生画像字典。
        job (JobTitleProfile): 岗位画像对象。

    Returns:
        float: 职业素养匹配得分，范围 0~1。
    """
    def score_match(student_val: Optional[float], job_val: Optional[float]) -> float:
        if student_val is None or job_val is None:
            return 1.0
        diff = abs(student_val - job_val)
        return max(0.0, 1.0 - diff / 5.0)

    innovation = score_match(student.get("innovation_score"), job.innovation_score)
    learning = score_match(student.get("learning_score"), job.learning_score)
    stress = score_match(student.get("stress_score"), job.stress_score)
    communication = score_match(student.get("communication_score"), job.communication_score)

    return (innovation + learning + stress + communication) / 4


def compute_potential_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """
    计算发展潜力匹配度（学习能力 + 实习经历）。

    Args:
        student (Dict[str, Any]): 学生画像字典。
        job (JobTitleProfile): 岗位画像对象。

    Returns:
        float: 发展潜力匹配得分，范围 0~1。
    """
    learning = student.get("learning_score", 0) / 5.0
    internship = 1.0 if student.get("internships") else 0.0
    return (learning + internship) / 2


# ================== 新增独立子维度计算函数 ==================
def compute_skill_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """技能匹配度（独立计算，基于学生技能与岗位技能的Jaccard相似度）"""
    student_skills = set(s.lower() for s in student.get("skills", []))
    job_skills_raw = job.skills
    if isinstance(job_skills_raw, str):
        job_skills = set(json.loads(job_skills_raw))
    else:
        job_skills = set(job_skills_raw)
    if not job_skills:
        return 1.0
    intersection = len(student_skills & job_skills)
    union = len(student_skills | job_skills)
    return intersection / union if union > 0 else 0.0

def compute_cert_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    stu_certs = set(c.lower().strip().replace(" ", "") for c in student.get("certificates", []))
    job_certs = set(c.lower().strip().replace(" ", "") for c in (job.certificates if isinstance(job.certificates, list) else json.loads(job.certificates)))
    if not job_certs:
        return 1.0
    # 只要学生有一个证书匹配岗位的任意一个证书即可（更宽松）
    for jc in job_certs:
        for sc in stu_certs:
            if jc in sc or sc in jc:
                return 1.0
    return 0.0

def compute_innovation_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """创新能力匹配度（独立）"""
    student_val = student.get("innovation_score", 0) / 5.0
    job_val = job.innovation_score / 5.0
    return 1.0 - abs(student_val - job_val)

def compute_learning_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """学习能力匹配度（独立）"""
    student_val = student.get("learning_score", 0) / 5.0
    job_val = job.learning_score / 5.0
    return 1.0 - abs(student_val - job_val)

def compute_stress_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """抗压能力匹配度（独立）"""
    student_val = student.get("stress_score", 0) / 5.0
    job_val = job.stress_score / 5.0
    return 1.0 - abs(student_val - job_val)

def compute_communication_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """沟通能力匹配度（独立）"""
    student_val = student.get("communication_score", 0) / 5.0
    job_val = job.communication_score / 5.0
    return 1.0 - abs(student_val - job_val)

def compute_education_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    stu_edu = student.get("education", "").strip()
    job_edu = job.education_required or ""
    if not job_edu or job_edu == "无要求":
        return 1.0
    # 标准化
    job_edu = job_edu.replace("及以上", "")
    if "本科" in job_edu and stu_edu in ["本科", "硕士", "博士"]:
        return 1.0
    if "硕士" in job_edu and stu_edu in ["硕士", "博士"]:
        return 1.0
    if "博士" in job_edu and stu_edu == "博士":
        return 1.0
    return 1.0 if stu_edu == job_edu else 0.0

def compute_major_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """专业匹配（独立）"""
    student_major = student.get("major", "").strip()
    job_major = job.major_required or ""
    if not job_major or job_major == "无要求":
        return 1.0
    return 1.0 if job_major in student_major else 0.0

def compute_experience_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """工作经验匹配（独立）"""
    student_exp = student.get("work_experience", "")
    job_exp = job.experience_required or ""
    if not job_exp or job_exp == "无要求":
        return 1.0
    job_year = 0
    match = re.search(r"\d+", job_exp)
    if match:
        job_year = int(match.group())
    stu_year = 0
    match = re.search(r"\d+", student_exp)
    if match:
        stu_year = int(match.group())
    return 1.0 if stu_year >= job_year else 0.0

def compute_language_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """语言匹配（独立）"""
    student_lang = student.get("language", "").lower()
    job_lang = (job.language_required or "").lower()
    if not job_lang or job_lang == "无要求":
        return 1.0
    return 1.0 if job_lang in student_lang else 0.0

def compute_internship_match(student: Dict[str, Any], job: JobTitleProfile) -> float:
    """实习要求匹配（独立）"""
    job_intern = job.internship_required or ""
    if "需要" in job_intern:
        return 1.0 if student.get("internships") else 0.0
    return 1.0


def compute_match(
    student_profile: Dict[str, Any],
    job_profile: JobTitleProfile,
) -> Dict[str, float]:
    """
    计算人岗匹配度，返回四个顶层维度和14个子维度得分。
    """
    base = compute_base_match(student_profile, job_profile)
    professional = compute_professional_match(student_profile, job_profile)
    quality = compute_quality_match(student_profile, job_profile)
    potential = compute_potential_match(student_profile, job_profile)

    total = base * 0.2 + professional * 0.4 + quality * 0.3 + potential * 0.1

    # 独立计算各子维度
    skill = compute_skill_match(student_profile, job_profile)
    cert = compute_cert_match(student_profile, job_profile)
    innovation = compute_innovation_match(student_profile, job_profile)
    learning = compute_learning_match(student_profile, job_profile)
    stress = compute_stress_match(student_profile, job_profile)
    communication = compute_communication_match(student_profile, job_profile)
    education = compute_education_match(student_profile, job_profile)
    major = compute_major_match(student_profile, job_profile)
    experience = compute_experience_match(student_profile, job_profile)
    language = compute_language_match(student_profile, job_profile)
    internship = compute_internship_match(student_profile, job_profile)

    return {
        "base_match": base,
        "professional_match": professional,
        "quality_match": quality,
        "potential_match": potential,
        "total_score": total,
        "skill_match": skill,
        "cert_match": cert,
        "innovation_match": innovation,
        "learning_match": learning,
        "stress_match": stress,
        "communication_match": communication,
        "education_match": education,
        "major_match": major,
        "experience_match": experience,
        "language_match": language,
        "internship_match": internship,
    }


def match_student_with_all_jobs(
    db: Session,
    student_id: int,
) -> List[Dict[str, Any]]:
    """
    计算指定学生与所有岗位的匹配度，按总分降序返回。

    Args:
        db (Session): 数据库会话。
        student_id (int): 学生 ID。

    Returns:
        List[Dict[str, Any]]: 匹配结果列表，每个元素包含 job_title, total_score, details。

    Raises:
        ValueError: 学生不存在时抛出。
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError("学生不存在")

    student_profile = student.profile_json
    job_profiles = db.query(JobTitleProfile).all()

    results = []
    for jp in job_profiles:
        job = db.query(Job).filter(Job.job_title == jp.job_title).first()
        if not job:
            continue
        details = compute_match(student_profile, jp)
        results.append(
            {
                "job_id": job.id,
                "job_title": jp.job_title,
                "total_score": details["total_score"],
                "details": details,
            }
        )

    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results