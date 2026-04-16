"""
学生画像生成服务模块

提供从简历文本生成结构化学生画像的功能，包括技能、能力评分、教育背景等字段的提取与验证。
"""
import json
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from app.core.llm_client import call_qwen
from app.core.resume_parser import parse_resume
from app.models.student import Student
from app.models.resume_version import ResumeVersion
from sqlalchemy import func


def validate_and_fix_student_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    校验并修复学生画像数据，确保字段完整、类型正确、数值在合理范围内。

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
        "internships",
        "education",
        "major",
        "work_experience",
        "language",
        "industry_background",
        "other_requirements",
        "overall_score",
        "overall_reason",
        "confidence_score",
        "confidence_reason",
    ]

    for field in required_fields:
        if field not in data:
            # 列表字段默认为空列表，字符串字段默认为空字符串
            if field in ["skills", "certificates", "internships"]:
                data[field] = []
            else:
                data[field] = ""

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

    # 总体评分 0~100
    try:
        overall = int(float(data.get("overall_score", 50)))
    except (ValueError, TypeError):
        overall = 50
    data["overall_score"] = max(0, min(100, overall))

    # 置信度处理：确保在 0~100 之间，并补齐默认值
    try:
        confidence = int(float(data.get("confidence_score", 80)))
    except (ValueError, TypeError):
        confidence = 80
    data["confidence_score"] = max(0, min(100, confidence))

    if not data.get("confidence_reason"):
        data["confidence_reason"] = ""

    # 学历标准化：将"本科"、"硕士"等关键词统一为规范表述
    edu = data.get("education", "")
    if edu:
        if "本科" in edu:
            data["education"] = "本科"
        elif "硕士" in edu:
            data["education"] = "硕士"

    return data


def generate_student_profile(
    resume_text: str,
    max_retries: int = 3,
    confidence_threshold: int = 70,
) -> Dict[str, Any]:
    """
    根据简历文本生成学生画像。

    调用大语言模型解析简历内容，提取结构化画像，并通过重试机制确保质量。

    Args:
        resume_text (str): 简历全文文本。
        max_retries (int, optional): 最大重试次数，默认 3。
        confidence_threshold (int, optional): 置信度阈值（0-100），低于该值将触发重试，默认 70。

    Returns:
        Dict[str, Any]: 学生画像字典。

    Raises:
        Exception: 当重试次数用尽仍无法生成有效画像时抛出。
    """
    prompt_template = """
你是一位职业顾问。请根据以下学生简历内容，分析该学生的就业能力画像。请严格按照下面的示例格式输出JSON。

示例：
简历内容：
张三，计算机科学与技术专业本科，熟悉Python、Java，有CET-6证书。在校期间参与过校园助手小程序开发，获得校级二等奖。在某某科技公司实习三个月，负责后端API开发。
输出：
{{
    "skills": ["Python", "Java"],
    "certificates": ["CET-6"],
    "innovation_score": 4,
    "innovation_reason": "参与过创新项目并获奖。",
    "learning_score": 4,
    "learning_reason": "能快速学习新技术。",
    "stress_score": 3,
    "stress_reason": "实习期间能承受一定压力。",
    "communication_score": 4,
    "communication_reason": "团队协作良好。",
    "internships": ["某某科技公司 后端开发实习"],
    "education": "本科",
    "major": "计算机科学与技术",
    "work_experience": "",
    "language": "英语CET-6",
    "industry_background": "",
    "other_requirements": "",
    "overall_score": 75,
    "overall_reason": "技术基础扎实，有项目经验，但缺少大型项目实践。",
    "confidence_score": 85,
    "confidence_reason": "简历内容完整，技能描述清晰。"
}}

现在请根据以下简历内容生成JSON：
简历内容：{resume_text}
"""
    system_prompt = "你是一位专业的职业顾问，擅长从简历中提取结构化信息并给出综合评价。"

    data = None
    for attempt in range(max_retries):
        try:
            user_prompt = prompt_template.format(resume_text=resume_text)
            result = call_qwen(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1200,
                temperature=0.3,
            )

            # 提取 JSON（取第一个 { 和最后一个 } 之间的内容）
            start = result.find("{")
            end = result.rfind("}") + 1
            json_str = result[start:end]
            data = json.loads(json_str)

            # 校验并修复数据
            data = validate_and_fix_student_profile(data)

            # 检查置信度，若达标则退出循环
            confidence = data.get("confidence_score", 0)
            if confidence >= confidence_threshold:
                break
            else:
                if attempt < max_retries - 1:
                    print(
                        f"学生画像置信度 {confidence} 低于阈值 {confidence_threshold}，"
                        f"重试第 {attempt + 2} 次"
                    )
                else:
                    print(
                        f"学生画像重试 {max_retries} 次后置信度仍为 {confidence}，"
                        "使用最后一次结果"
                    )
        except Exception as e:
            print(f"学生画像生成尝试 {attempt + 1} 失败: {e}")
            if attempt == max_retries - 1:
                raise
            continue

    if data is None:
        raise Exception("学生画像生成失败")
    return data


def create_student_from_resume(db: Session, name: str, file_path: str) -> Student:
    # ... 解析简历文本和生成画像 ...
    resume_text = parse_resume(file_path)
    profile = generate_student_profile(resume_text)

    # 检查学生是否存在（如果不存在则创建）
    student = db.query(Student).filter(Student.name == name).first()
    if not student:
        student = Student(name=name, resume_text=resume_text, profile_json=profile)
        db.add(student)
        db.flush()  # 获取 student.id
        version = 1
    else:
        # 更新现有学生记录
        student.resume_text = resume_text
        student.profile_json = profile
        # 获取当前最大版本号
        max_version = db.query(func.max(ResumeVersion.version)).filter(
            ResumeVersion.student_id == student.id
        ).scalar() or 0
        version = max_version + 1

    # 保存历史版本
    version_record = ResumeVersion(
        student_id=student.id,
        version=version,
        resume_text=resume_text,
        profile_json=profile
    )
    db.add(version_record)
    db.commit()
    db.refresh(student)
    return student

def parse_free_text(text: str, type: str) -> dict:
    """
    解析用户自由输入的文本，返回结构化的经历条目或基本信息。
    type: "project", "paper", "internship", "competition", "basic"
    """
    system_prompt = "你是一位信息提取专家，擅长从文本中提取结构化信息。"
    if type == "basic":
        user_prompt = f"""
请从以下文本中提取学生的基本信息：意向城市、性别、学校、年级。
输出JSON格式，例如：
{{"intended_city": "上海", "gender": "男", "school": "复旦大学", "grade": "大三"}}
文本：{text}
"""
    else:
        user_prompt = f"""
请从以下文本中提取{type}相关的经历信息，输出JSON格式。
- name: 项目/论文/实习/竞赛名称
- role: 角色（可选）
- description: 简要描述
- technologies: 使用的技术（列表，可选）
文本：{text}
"""
    try:
        result = call_qwen(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.3
        )
        start = result.find('{')
        end = result.rfind('}') + 1
        json_str = result[start:end]
        data = json.loads(json_str)
        return data
    except Exception as e:
        raise Exception(f"解析失败: {e}")

def finalize_student_profile(profile: dict) -> dict:
    """
    根据学生已有的基本信息、经历、技能等，调用大模型生成完整的画像。
    返回更新后的 profile 字典。
    """
    # 构造提示词
    manual_basics = profile.get("manual_basics", {})
    experiences = profile.get("experiences", {})
    current_skills = profile.get("skills", [])
    current_certs = profile.get("certificates", [])

    prompt = f"""
你是一位职业分析师。请根据以下学生信息，生成其完整的就业能力画像。输出JSON格式，包含以下字段：
- skills: 技能列表（基于学生已有技能和经历中体现的技术）
- certificates: 证书列表
- innovation_score: 0-5之间的整数，创新能力评分
- innovation_reason: 简短理由
- learning_score: 0-5整数，学习能力评分
- learning_reason: 简短理由
- stress_score: 0-5整数，抗压能力评分
- stress_reason: 简短理由
- communication_score: 0-5整数，沟通能力评分
- communication_reason: 简短理由
- internships: 实习经历列表（从经历中提取）
- education: 学历（可从手动信息或默认值）
- major: 专业（可从手动信息或默认值）
- work_experience: 工作经验（从经历中提取）
- language: 语言能力
- industry_background: 行业背景（根据项目/实习推断）
- other_requirements: 其他
- overall_score: 0-100整数，综合竞争力评分
- overall_reason: 评分理由

学生信息：
- 基本信息：{json.dumps(manual_basics, ensure_ascii=False)}
- 已有技能：{', '.join(current_skills)}
- 已有证书：{', '.join(current_certs)}
- 项目经历：{json.dumps(experiences.get('projects', []), ensure_ascii=False)}
- 论文经历：{json.dumps(experiences.get('papers', []), ensure_ascii=False)}
- 实习经历：{json.dumps(experiences.get('internships', []), ensure_ascii=False)}
- 竞赛经历：{json.dumps(experiences.get('competitions', []), ensure_ascii=False)}

请直接返回JSON，不要包含其他文字。
"""
    result = call_qwen(
        user_prompt=prompt,
        system_prompt="你是一位专业的职业分析师。",
        max_tokens=1000,
        temperature=0.3
    )
    start = result.find('{')
    end = result.rfind('}') + 1
    json_str = result[start:end]
    data = json.loads(json_str)

    # 合并到原 profile（保留 manual_basics 和 experiences）
    profile.update(data)
    # 确保 manual_basics 和 experiences 不被覆盖（它们不在 data 中，但为防止万一，重新赋值）
    profile["manual_basics"] = manual_basics
    profile["experiences"] = experiences
    return profile

def regenerate_profile_scores(profile: dict) -> dict:
    """根据学生画像（技能、经历等）重新生成能力评分和理由"""
    skills = profile.get("skills", [])
    certificates = profile.get("certificates", [])
    internships = profile.get("internships", [])
    projects = profile.get("experiences", {}).get("projects", [])
    competitions = profile.get("experiences", {}).get("competitions", [])
    work_experience = profile.get("work_experience", "")
    language = profile.get("language", "")
    education = profile.get("education", "")
    major = profile.get("major", "")

    prompt = f"""
你是一位职业能力评估专家。请根据以下学生的个人信息，评估其在五个维度的能力得分（0-5分）以及综合竞争力得分（0-100分），并给出简短理由。

学生信息：
- 教育背景：{education}，专业：{major}
- 技能：{', '.join(skills) if skills else '无'}
- 证书：{', '.join(certificates) if certificates else '无'}
- 实习经历：{', '.join(internships) if internships else '无'}
- 项目经历：{', '.join([p.get('name', '') for p in projects]) if projects else '无'}
- 竞赛经历：{', '.join([c.get('name', '') for c in competitions]) if competitions else '无'}
- 工作/社团经历：{work_experience or '无'}
- 语言能力：{language or '无'}

请输出 JSON 格式，包含以下字段：
{{
    "innovation_score": 整数0-5,
    "innovation_reason": "理由",
    "learning_score": 整数0-5,
    "learning_reason": "理由",
    "stress_score": 整数0-5,
    "stress_reason": "理由",
    "communication_score": 整数0-5,
    "communication_reason": "理由",
    "overall_score": 整数0-100,
    "overall_reason": "综合理由",
    "confidence_score": 整数0-100,
    "confidence_reason": "置信度理由"
}}
只返回 JSON。
"""
    try:
        from app.core.llm_client import call_qwen
        result = call_qwen(user_prompt=prompt, system_prompt="你是一位职业能力评估专家。", max_tokens=800, temperature=0.3)
        import json, re
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            new_scores = json.loads(match.group())
        else:
            raise ValueError("No JSON found")
    except Exception as e:
        print(f"重新生成评分失败: {e}")
        new_scores = {
            "innovation_score": profile.get("innovation_score", 3),
            "innovation_reason": profile.get("innovation_reason", ""),
            "learning_score": profile.get("learning_score", 3),
            "learning_reason": profile.get("learning_reason", ""),
            "stress_score": profile.get("stress_score", 3),
            "stress_reason": profile.get("stress_reason", ""),
            "communication_score": profile.get("communication_score", 3),
            "communication_reason": profile.get("communication_reason", ""),
            "overall_score": profile.get("overall_score", 60),
            "overall_reason": profile.get("overall_reason", ""),
            "confidence_score": profile.get("confidence_score", 80),
            "confidence_reason": profile.get("confidence_reason", "")
        }
    profile.update(new_scores)
    return profile