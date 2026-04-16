from sqlalchemy.orm import Session
from app.models.user import User
from app.models.student import Student
from app.schemas.user import UserRegisterRequest
from app.core.auth import get_password_hash, verify_password, create_access_token

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_user(db: Session, user_data: UserRegisterRequest) -> User:
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise ValueError("用户名已存在")

    # 确定学生记录
    if user_data.studentId:
        student = db.query(Student).filter(Student.id == user_data.studentId).first()
        if not student:
            raise ValueError("学生 ID 不存在")
        student_id = student.id
    else:
        # 创建新的学生记录，并初始化 profile_json 结构
        student = Student(
            name=user_data.username,
            resume_text="",
            profile_json={
                "skills": [],
                "certificates": [],
                "innovation_score": 0,
                "learning_score": 0,
                "stress_score": 0,
                "communication_score": 0,
                "internships": [],
                "education": "",
                "major": "",
                "work_experience": "",
                "language": "",
                "industry_background": "",
                "other_requirements": "",
                "overall_score": 0,
                "overall_reason": "",
                "confidence_score": 0,
                "confidence_reason": "",
                "manual_basics": {
                    "intended_city": "",
                    "gender": "",
                    "school": "",
                    "grade": ""
                },
                "experiences": {
                    "projects": [],
                    "papers": [],
                    "internships": [],
                    "competitions": []
                }
            }
        )
        db.add(student)
        db.flush()
        student_id = student.id

    # 创建用户记录
    user = User(
        username=user_data.username,
        password=get_password_hash(user_data.password),
        email=user_data.email,
        role=user_data.role,
        student_id=student_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def build_user_response(user: User):
    return {
        "username": user.username,
        "role": user.role,
        "studentId": user.student_id
    }