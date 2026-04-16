# batch_test_accuracy.py
import sys
import os
import time
import json
import random
import tempfile
from typing import List
import requests
from docx import Document
from dotenv import load_dotenv
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# 加载环境变量（数据库连接）
load_dotenv()

# ----------------------------- 配置 -----------------------------
API_BASE = "http://127.0.0.1:8000/api/v1"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "123456"


# ----------------------------- 1. 解析 Word 文档 -----------------------------
def parse_resumes_from_word(file_path: str) -> List[str]:
    doc = Document(file_path)
    full_text = '\n'.join([para.text for para in doc.paragraphs])

    # 按“姓名”行分割：匹配以2-4个汉字开头，后跟换行符
    import re
    # 分割点：行首为2-4个汉字，且该行后紧跟“求职意向”或“基本信息”（可选）
    # 使用正向预查，保留分割点
    blocks = re.split(r'(?=^[\u4e00-\u9fa5]{2,4}\n)', full_text, flags=re.MULTILINE)
    # 过滤掉空块或过短的块
    resumes = [block.strip() for block in blocks if len(block.strip()) > 50]
    return resumes


# ----------------------------- 2. 上传简历 -----------------------------
def login() -> str:
    resp = requests.post(f"{API_BASE}/auth/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise Exception("登录失败")
    return data["token"]


def upload_resume(token: str, resume_text: str, idx: int) -> bool:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(resume_text)
        temp_path = f.name
    try:
        with open(temp_path, 'rb') as f:
            files = {'file': f}
            headers = {'Authorization': f'Bearer {token}'}
            resp = requests.post(f"{API_BASE}/students/upload", headers=headers, files=files)
        if resp.status_code == 200:
            print(f"✅ 已上传第 {idx + 1} 份简历")
            return True
        else:
            print(f"❌ 第 {idx + 1} 份简历上传失败: {resp.text}")
            return False
    finally:
        os.unlink(temp_path)


def batch_upload(resumes: List[str]) -> int:
    token = login()
    success_count = 0
    for i, text in enumerate(resumes):
        if upload_resume(token, text, i):
            success_count += 1
        time.sleep(0.3)
    return success_count


# ----------------------------- 3. 准确度评估 -----------------------------
def get_db_session():
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "career_agent")
    DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


# 将项目路径加入 sys.path 以便导入 app 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models.student import Student
from app.models.job import JobTitleProfile
from app.services.matching import compute_match, compute_skill_match, compute_education_match, compute_major_match, \
    compute_cert_match


def test_skill_accuracy(session):
    students = session.query(Student).order_by(func.random()).limit(3).all()
    if len(students) < 3:
        raise ValueError("学生不足3人")
    job_profiles = session.query(JobTitleProfile).all()
    if not job_profiles:
        raise ValueError("岗位画像为空")
    total_rate = 0.0
    for student in students:
        scores = []
        for jp in job_profiles:
            details = compute_match(student.profile_json, jp)
            scores.append((jp, details["total_score"]))
        scores.sort(key=lambda x: x[1], reverse=True)
        top_3 = [jp for jp, _ in scores[:3]]
        skill_rates = [compute_skill_match(student.profile_json, jp) for jp in top_3]
        student_rate = sum(skill_rates) / len(skill_rates)
        total_rate += student_rate
    return total_rate / 3


def test_info_accuracy(session):
    all_students = session.query(Student).all()
    job_profiles = session.query(JobTitleProfile).all()
    matched_students = []
    for student in all_students:
        for jp in job_profiles:
            details = compute_match(student.profile_json, jp)
            if details["total_score"] > 0:
                matched_students.append(student)
                break
    if len(matched_students) < 10:
        sampled = matched_students
    else:
        sampled = random.sample(matched_students, 10)
    correct = 0
    for student in sampled:
        best_score = -1
        best_jp = None
        for jp in job_profiles:
            details = compute_match(student.profile_json, jp)
            if details["total_score"] > best_score:
                best_score = details["total_score"]
                best_jp = jp
        if not best_jp:
            continue
        edu_ok = compute_education_match(student.profile_json, best_jp) == 1.0
        major_ok = compute_major_match(student.profile_json, best_jp) == 1.0
        cert_ok = compute_cert_match(student.profile_json, best_jp) == 1.0
        if edu_ok and major_ok and cert_ok:
            correct += 1
    return correct / len(sampled)


def generate_accuracy_report(session):
    skill_acc = test_skill_accuracy(session)
    info_acc = test_info_accuracy(session)
    report = {
        "skill_match_accuracy": round(skill_acc, 4),
        "skill_match_passed": skill_acc >= 0.8,
        "info_accuracy": round(info_acc, 4),
        "info_passed": info_acc >= 0.9,
        "overall_passed": skill_acc >= 0.8 and info_acc >= 0.9,
        "test_details": {
            "skill_sample_size": 3,
            "info_sample_size": min(10, len([s for s in session.query(Student).all() if any(
                compute_match(s.profile_json, jp)["total_score"] > 0 for jp in session.query(JobTitleProfile).all())])),
            "calculation_method": {
                "skill_match": "随机抽取3名学生，每名学生取匹配度最高的前3个岗位，计算技能匹配率（学生技能与岗位技能的交集/岗位技能数），取3名学生的平均匹配率",
                "info_accuracy": "随机抽取10名有匹配结果的学生（不足则全取），检查其学历、专业、证书与最佳匹配岗位的要求是否完全一致（岗位要求为空时视为匹配），计算完全符合的比例"
            }
        }
    }
    with open("accuracy_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("准确度报告已生成: accuracy_report.json")
    print(f"关键技能匹配准确率: {skill_acc:.2%} {'通过' if skill_acc >= 0.8 else '不通过'}")
    print(f"关键信息准确率: {info_acc:.2%} {'通过' if info_acc >= 0.9 else '不通过'}")


# ----------------------------- 主流程 -----------------------------
def main():
    # 如果没有提供命令行参数，则使用默认文件名
    if len(sys.argv) < 2:
        word_file = "resumes.docx"
        print(f"未指定文件，使用默认路径: {word_file}")
    else:
        word_file = sys.argv[1]

    # 检查文件是否存在
    if not os.path.exists(word_file):
        print(f"文件不存在: {word_file}")
        sys.exit(1)

    print("正在解析 Word 文档...")
    resumes = parse_resumes_from_word(word_file)
    print(f"共解析出 {len(resumes)} 份简历")

    # 可选：只测试前 N 份（避免时间过长）
    resumes = resumes[:20]

    print("开始批量上传简历...")
    success = batch_upload(resumes)
    print(f"上传完成，成功 {success} 份，失败 {len(resumes) - success} 份")

    print("等待数据库处理完成...")
    time.sleep(5)  # 等待后端异步处理

    print("开始评估准确度...")
    session = get_db_session()
    generate_accuracy_report(session)
    session.close()


if __name__ == "__main__":
    main()