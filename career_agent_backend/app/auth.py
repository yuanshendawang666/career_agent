from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from app.database import get_db
from app import models, schemas

load_dotenv()

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=schemas.LoginResponse)
def register(user: schemas.UserRegisterRequest, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    hashed_pw = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_pw,
        role=user.role,
        studentId=user.studentId
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 生成 token
    access_token = create_access_token(data={"sub": db_user.username})
    return schemas.LoginResponse(
        success=True,
        user=schemas.UserResponse(username=db_user.username, role=db_user.role, studentId=db_user.studentId),
        token=access_token,
        message="注册成功"
    )

@router.post("/login", response_model=schemas.LoginResponse)
def login(user: schemas.UserLoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    access_token = create_access_token(data={"sub": db_user.username})
    return schemas.LoginResponse(
        success=True,
        user=schemas.UserResponse(username=db_user.username, role=db_user.role, studentId=db_user.studentId),
        token=access_token,
        message="登录成功"
    )