import os
import re
import json
from PyPDF2 import PdfReader
from docx import Document
import dashscope
from app.core.config import settings

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def parse_resume(file_path: str, ext: str) -> str:
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("不支持的文件格式")

def generate_profile_from_resume(resume_text: str) -> dict:
    """调用通义千问生成结构化画像，返回字典"""
    prompt = f"""
你是一个职业规划助手。请根据以下简历内容，提取学生的结构化信息，以 JSON 格式返回。
JSON 应包含以下字段（如果信息缺失则使用空值或空列表）：
- name: 姓名
- skills: 技能列表（字符串数组）
- certificates: 证书列表
- education: 最高学历（如"本科"、"硕士"）
- major: 专业
- intended_city: 意向城市
- experiences: 对象，包含 projects, papers, internships, competitions 四个数组，每个元素含 name, role, description, technologies

简历内容：
{resume_text}

只返回 JSON，不要有其他解释。
"""
    try:
        response = dashscope.Generation.call(
            model=settings.qwen_model,
            messages=[{"role": "user", "content": prompt}],
            result_format="message"
        )
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            # 提取 JSON（可能被 markdown 包裹）
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            return json.loads(content)
        else:
            # 降级返回默认结构
            return {"name": "", "skills": [], "certificates": [], "education": "", "major": "", "intended_city": "", "experiences": {"projects": [], "papers": [], "internships": [], "competitions": []}}
    except Exception:
        return {"name": "", "skills": [], "certificates": [], "education": "", "major": "", "intended_city": "", "experiences": {"projects": [], "papers": [], "internships": [], "competitions": []}}