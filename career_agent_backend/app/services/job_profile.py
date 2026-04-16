"""
岗位画像生成服务模块

提供根据职位描述生成结构化岗位画像的功能，包括技能、能力评分、学历要求等字段的提取与验证。
"""
import json
import re
from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session

from app.core.llm_client import call_qwen
from app.models.job import Job, JobProfile


def validate_and_fix_job_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    校验并修复岗位画像数据，确保字段完整、类型正确、数值在合理范围内。

    Args:
        data (Dict[str, Any]): 从 LLM 解析得到的原始画像字典。

    Returns:
        Dict[str, Any]: 修复后的画像字典，包含所有必需字段。
    """
    # 必需字段列表，缺失时提供默认值
    required_fields = [
        "skills",
        "certificates",
        "innovation_score",
        "innovation_reason",
        "learning_score",
        "learning_reason",
        "stress_score",
        "stress_reason",
        "communication_score",
        "communication_reason",
        "internship_required",
        "education_required",
        "major_required",
        "experience_required",
        "language_required",
        "industry_background",
        "other_requirements",
        "confidence_score",
        "confidence_reason",
    ]

    for field in required_fields:
        if field not in data:
            # 列表字段默认为空列表，字符串字段默认为空字符串
            data[field] = [] if field in ["skills", "certificates"] else ""

    # 技能去重并限制最多 20 个
    if isinstance(data["skills"], list):
        data["skills"] = list(dict.fromkeys(data["skills"]))[:20]

    # 确保能力评分在 0~5 之间（整数）
    score_fields = [
        "innovation_score",
        "learning_score",
        "stress_score",
        "communication_score",
    ]
    for field in score_fields:
        try:
            val = int(float(data[field]))
        except (ValueError, TypeError):
            val = 0
        data[field] = max(0, min(5, val))

    # 置信度处理：确保在 0~100 之间，并补齐默认值
    try:
        confidence = int(float(data.get("confidence_score", 80)))
    except (ValueError, TypeError):
        confidence = 80
    data["confidence_score"] = max(0, min(100, confidence))

    if not data.get("confidence_reason"):
        data["confidence_reason"] = ""

    # 学历标准化：将"本科"、"硕士"等关键词统一为规范表述
    edu = data.get("education_required", "")
    if edu:
        if "本科" in edu:
            data["education_required"] = "本科及以上"
        elif "硕士" in edu:
            data["education_required"] = "硕士及以上"

    return data


def generate_job_profile(
    db: Session,
    job_id: int,
    max_retries: int = 3,
    confidence_threshold: int = 70,
) -> JobProfile:
    """
    根据岗位 ID 生成对应的岗位画像，并存入数据库。

    该函数调用大语言模型解析职位描述，提取结构化画像，并通过重试机制确保质量。
    生成结果存入 job_profiles 表，并返回 ORM 对象。

    Args:
        db (Session): 数据库会话。
        job_id (int): 岗位 ID。
        max_retries (int, optional): 最大重试次数，默认 3。
        confidence_threshold (int, optional): 置信度阈值（0-100），低于该值将触发重试，默认 70。

    Returns:
        JobProfile: 已持久化的岗位画像 ORM 对象。

    Raises:
        ValueError: 当岗位不存在时抛出。
        Exception: 当重试次数用尽仍无法生成有效画像时抛出。
    """
    # 查询岗位信息
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise ValueError("Job not found")

    system_prompt = "你是一位职业分析师，擅长从职位描述中提取结构化的岗位要求信息。"

    user_prompt_template = """
请根据以下职位描述，提取该岗位的详细画像要求。请严格按照下面的示例格式输出JSON。

示例：
职位描述：负责公司Java后端开发，要求精通Spring Boot、MySQL，有微服务经验优先。本科以上学历，计算机相关专业，3年以上工作经验。
输出：
{{
    "skills": ["Java", "Spring Boot", "MySQL", "微服务"],
    "certificates": [],
    "innovation_score": 3,
    "innovation_reason": "需要根据业务需求进行技术选型，有一定创新空间。",
    "learning_score": 4,
    "learning_reason": "需学习新框架和微服务技术。",
    "stress_score": 3,
    "stress_reason": "项目节奏适中，压力一般。",
    "communication_score": 4,
    "communication_reason": "需与产品、前端协作。",
    "internship_required": "无要求",
    "education_required": "本科及以上",
    "major_required": "计算机相关专业",
    "experience_required": "3年以上",
    "language_required": "",
    "industry_background": "",
    "other_requirements": "",
    "confidence_score": 90,
    "confidence_reason": "职位描述详细，技能和要求明确。"
}}

现在请根据以下职位描述生成JSON：
职位描述：{job_description}
"""

    data = None
    for attempt in range(max_retries):
        try:
            # 构建提示词
            user_prompt = user_prompt_template.format(
                job_description=job.job_description
            )

            # 调用 LLM
            result = call_qwen(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                temperature=0.3,
            )

            # 提取 JSON（取第一个 { 和最后一个 } 之间的内容）
            start = result.find("{")
            end = result.rfind("}") + 1
            json_str = result[start:end]
            data = json.loads(json_str)

            # 校验并修复数据
            data = validate_and_fix_job_profile(data)

            # 检查置信度，若达标则退出循环
            confidence = data.get("confidence_score", 0)
            if confidence >= confidence_threshold:
                break
            else:
                if attempt < max_retries - 1:
                    print(
                        f"Job {job_id} 置信度 {confidence} 低于阈值 {confidence_threshold}，"
                        f"重试第 {attempt + 2} 次"
                    )
                else:
                    print(
                        f"Job {job_id} 重试 {max_retries} 次后置信度仍为 {confidence}，"
                        "使用最后一次结果"
                    )
        except Exception as e:
            print(f"Job {job_id} 尝试 {attempt + 1} 失败: {e}")
            if attempt == max_retries - 1:
                raise
            continue

    if data is None:
        raise Exception(f"Job {job_id} 生成画像失败")

    # 将 JSON 字段转换为字符串存储
    profile = JobProfile(
        job_id=job_id,
        skills=json.dumps(data["skills"], ensure_ascii=False),
        certificates=json.dumps(data.get("certificates", []), ensure_ascii=False),
        innovation_score=data["innovation_score"],
        innovation_reason=data["innovation_reason"],
        learning_score=data["learning_score"],
        learning_reason=data["learning_reason"],
        stress_score=data["stress_score"],
        stress_reason=data["stress_reason"],
        communication_score=data["communication_score"],
        communication_reason=data["communication_reason"],
        internship_required=data["internship_required"],
        education_required=data.get("education_required", ""),
        major_required=data.get("major_required", ""),
        experience_required=data.get("experience_required", ""),
        language_required=data.get("language_required", ""),
        industry_background=data.get("industry_background", ""),
        other_requirements=data.get("other_requirements", ""),
        confidence_score=data["confidence_score"],
        confidence_reason=data["confidence_reason"],
    )

    # 存入数据库
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile